import contextlib
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest
import urllib.error
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / ".forgejo/scripts/ai-review.py"
OWN = "example/rules"
ENV = {"FORGEJO_URL": "https://forgejo.example", "REPO": OWN, "TOKEN": "job"}
with mock.patch.dict(os.environ, ENV):
    spec = importlib.util.spec_from_file_location("ai_review", SCRIPT)
    ai_review = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ai_review)

ISSUES = {
    "example/rules/issues/2": {"title": "Move CI", "state": "open", "body": "move it"},
    "example/rules/issues/3": {"title": "Long", "state": "open", "body": "x" * 50000},
    "example/private-app/issues/12": {"title": "private plans", "state": "open", "body": "secret scope"},
    "example/public-app/issues/5": {"title": "public bug", "state": "open", "body": "it crashes"},
}
ALL = [{"user": {"login": "maintainer"}, "body": f"comment {i}"} for i in range(57)]
COMMENTS = {
    "example/rules/issues/2/comments?limit=50&page=1": ALL[:50],
    "example/rules/issues/2/comments?limit=50&page=2": ALL[50:],
    "example/rules/issues/3/comments?limit=50&page=1":
        [{"user": {"login": "maintainer"}, "body": "Decision: latest"}],
    "example/private-app/issues/12/comments?limit=50&page=1": [],
    "example/public-app/issues/5/comments?limit=50&page=1": [],
}
PRIVATE_REPOS = {"example/private-app"}


def fake_server(calls, own_private):
    def urlopen(req, timeout):
        path = req.full_url.split("/api/v1/repos/", 1)[1]
        auth = req.get_header("Authorization")
        token = auth.split()[1] if auth else None
        calls.append((path, token))
        if path == OWN:
            return io.BytesIO(json.dumps({"private": own_private}).encode())
        repo = "/".join(path.split("/")[:2])
        data = ISSUES.get(path, COMMENTS.get(path))
        hidden = ((token == "job" and repo != OWN)
                  or (token is None and repo in PRIVATE_REPOS)
                  or data is None)
        if hidden:
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b""))
        return io.BytesIO(json.dumps(data).encode())
    return urlopen


class RepoRulesTest(unittest.TestCase):
    def setUp(self):
        self.cwd = pathlib.Path.cwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def write(self, path, text):
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text(text)

    def test_rules_come_with_the_script_and_never_from_the_checkout(self):
        self.write(".forgejo/RULES.md", "stale copy")
        self.write("RULES.md", "repo's own RULES.md")
        self.write("CONTRIBUTING.md", "run pytest")
        self.write("README.md", "what it is")
        text = ai_review.repo_rules()
        canonical = (SCRIPT.parents[2] / "RULES.md").read_text()
        self.assertTrue(text.startswith("## Project rules (RULES.md)\n" + canonical))
        self.assertNotIn("stale copy", text)
        self.assertNotIn("repo's own RULES.md", text)
        self.assertIn("run pytest", text)
        self.assertIn("what it is", text)

    def test_missing_rules_fail_the_check_without_asking_the_model(self):
        # The fetched tree has the script but no RULES.md; the repo still has an old copy.
        gate = pathlib.Path(self.tmp.name, "gate/.forgejo/scripts/ai-review.py")
        self.write(gate, SCRIPT.read_text())
        self.write(".forgejo/RULES.md", "stale copy")
        with mock.patch.dict(os.environ, ENV):
            spec = importlib.util.spec_from_file_location("ai_review_without_rules", gate)
            review = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(review)

        def api(method, path, body=None, raw=False):
            if raw:
                return "diff --git a/x b/x\n"
            return {"head": {"sha": "abc"}, "state": "open", "title": "t", "body": ""}

        statuses = []
        model = mock.Mock(return_value='{"summary": "fine", "findings": []}')
        with (mock.patch.dict(os.environ, {**ENV, "PR": "7", "AI_REVIEW": "required"}),
              mock.patch.object(review, "api", api),
              mock.patch.object(review, "pages", lambda path: iter(())),
              mock.patch.object(review, "set_status", lambda *a: statuses.append(a)),
              mock.patch.object(review, "ask_model", model),
              contextlib.redirect_stdout(io.StringIO())):
            try:
                review.main()
                code = None
            except SystemExit as e:
                code = e.code
        model.assert_not_called()
        self.assertEqual(statuses[-1][1], "error")
        self.assertIn("FileNotFoundError", statuses[-1][2])
        self.assertTrue(code)

    def test_other_missing_files_say_none(self):
        text = ai_review.repo_rules()
        self.assertIn("## CONTRIBUTING.md\nnone", text)
        self.assertIn("## README.md (what the project is)\nnone", text)


class LinkedIssuesTest(unittest.TestCase):
    def run_linked(self, body, read_token="reader", own_private=True):
        env = dict(ENV)
        if read_token:
            env["ISSUE_READ_TOKEN"] = read_token
        calls = []
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(ai_review.urllib.request, "urlopen", fake_server(calls, own_private)):
            text = ai_review.linked_issues(body)
        return text, [c for c in calls if c[0] != OWN]

    def test_same_repo_issue_with_its_last_ten_comments_across_pages(self):
        text, calls = self.run_linked("Closes #2")
        self.assertIn("#2 Move CI (open)\nmove it", text)
        shown = [line for line in text.splitlines() if line.startswith("- maintainer: ")]
        self.assertEqual(shown, [f"- maintainer: comment {i}" for i in range(47, 57)])
        self.assertEqual({t for _, t in calls}, {"job"})

    def test_long_body_keeps_latest_comment(self):
        text, _ = self.run_linked("Closes #3")
        self.assertIn("- maintainer: Decision: latest", text)
        self.assertLess(len(text), 9000)

    def test_private_repo_reads_other_repos_with_read_token(self):
        text, calls = self.run_linked("Refs example/private-app#12")
        self.assertIn("example/private-app#12 private plans (open)\nsecret scope", text)
        self.assertEqual({t for _, t in calls}, {"reader"})

    def test_public_repo_never_quotes_a_private_issue(self):
        text, calls = self.run_linked("Refs example/private-app#12", own_private=False)
        self.assertNotIn("secret scope", text)
        self.assertNotIn("private plans", text)
        self.assertIn("example/private-app#12: could not be read (HTTP 404)", text)
        self.assertEqual({t for _, t in calls}, {None})

    def test_public_repo_reads_public_issues_anonymously(self):
        text, calls = self.run_linked("Refs example/public-app#5", own_private=False)
        self.assertIn("public bug (open)\nit crashes", text)
        self.assertEqual({t for _, t in calls}, {None})

    def test_private_repo_without_token_names_the_issue_without_fetching(self):
        text, calls = self.run_linked("Refs example/private-app#12", read_token=None)
        self.assertIn("not readable here", text)
        self.assertEqual(calls, [])

    def test_missing_issue_is_reported_not_raised(self):
        text, _ = self.run_linked("Closes #99")
        self.assertIn("#99: could not be read (HTTP 404)", text)

    def test_server_error_fails_closed(self):
        calls = []
        inner = fake_server(calls, True)

        def flaky(req, timeout):
            if "/issues/" in req.full_url:
                raise urllib.error.HTTPError(req.full_url, 503, "Unavailable", {}, io.BytesIO(b""))
            return inner(req, timeout)
        with mock.patch.dict(os.environ, dict(ENV), clear=True), \
                mock.patch.object(ai_review.urllib.request, "urlopen", flaky), \
                self.assertRaises(urllib.error.HTTPError):
            ai_review.linked_issues("Closes #2")

    def test_no_refs(self):
        text, calls = self.run_linked("just a change")
        self.assertEqual(text, "none named")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
