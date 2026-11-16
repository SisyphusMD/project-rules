import importlib.util
import io
import json
import os
import pathlib
import unittest
import urllib.error
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / ".forgejo/scripts/issue-link.py"
spec = importlib.util.spec_from_file_location("issue_link", SCRIPT)
issue_link = importlib.util.module_from_spec(spec)
spec.loader.exec_module(issue_link)

OWN = "example/rules"
ISSUES = {
    "example/rules/issues/2": {"title": "Move CI", "state": "open"},
    "example/rules/issues/10": {"title": "a PR", "state": "closed", "pull_request": {"merged": True}},
    "example/private-app/issues/12": {"title": "private plans", "state": "open"},
    "example/public-app/issues/5": {"title": "public bug", "state": "open"},
}
PRIVATE_REPOS = {"example/private-app"}


class FakeServer:
    """Answers like Forgejo: the job token sees only its own repo, an anonymous caller sees only
    public repos, and the read token sees everything."""

    def __init__(self, own_private):
        self.own_private = own_private
        self.calls = []

    def __call__(self, req, timeout):
        path = req.full_url.split("/api/v1/repos/", 1)[1]
        auth = req.get_header("Authorization")
        token = auth.split()[1] if auth else None
        self.calls.append((path, token))
        if path == OWN:
            return io.BytesIO(json.dumps({"private": self.own_private}).encode())
        repo = "/".join(path.split("/")[:2])
        hidden = ((token == "job" and repo != OWN)
                  or (token is None and repo in PRIVATE_REPOS)
                  or path not in ISSUES)
        if hidden:
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b""))
        return io.BytesIO(json.dumps(ISSUES[path]).encode())


class IssueLinkTest(unittest.TestCase):
    def run_main(self, body, read_token="reader", own_private=True):
        env = {"FORGEJO_URL": "https://forgejo.example", "REPO": OWN, "TOKEN": "job", "PR_BODY": body}
        if read_token:
            env["ISSUE_READ_TOKEN"] = read_token
        server = FakeServer(own_private)
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(issue_link.urllib.request, "urlopen", server):
            issue_link.main()
        return [c for c in server.calls if c[0] != OWN]

    def test_same_repo_ref_uses_job_token(self):
        self.assertEqual(self.run_main("Closes #2"), [("example/rules/issues/2", "job")])

    def test_private_repo_reads_other_repos_with_read_token(self):
        calls = self.run_main("Refs example/private-app#12")
        self.assertEqual(calls, [("example/private-app/issues/12", "reader")])

    def test_public_repo_never_sends_the_read_token(self):
        calls = self.run_main("Refs example/public-app#5", own_private=False)
        self.assertEqual(calls, [("example/public-app/issues/5", None)])

    def test_public_repo_cannot_see_a_private_issue(self):
        with self.assertRaises(SystemExit) as e:
            self.run_main("Refs example/private-app#12", own_private=False)
        self.assertIn("example/private-app#12 does not exist or is private", str(e.exception.code))

    def test_own_repo_written_out_counts_as_same_repo(self):
        self.assertEqual(self.run_main("Closes Example/Rules#2"), [("example/rules/issues/2", "job")])

    def test_mixed_refs_all_checked(self):
        calls = self.run_main("Closes #2\nRefs example/private-app#12")
        self.assertEqual(sorted(p for p, _ in calls),
                         ["example/private-app/issues/12", "example/rules/issues/2"])

    def test_no_ref_fails(self):
        with self.assertRaises(SystemExit) as e:
            self.run_main("Fixes the thing")
        self.assertIn("owner/repo#n", str(e.exception.code))

    def test_missing_cross_repo_issue_fails(self):
        with self.assertRaises(SystemExit) as e:
            self.run_main("Refs example/private-app#999")
        self.assertIn("example/private-app#999 does not exist", str(e.exception.code))

    def test_pr_number_fails(self):
        with self.assertRaises(SystemExit) as e:
            self.run_main("Closes #10")
        self.assertIn("#10 is a PR", str(e.exception.code))

    def test_private_repo_without_read_token_fails_clearly(self):
        with self.assertRaises(SystemExit) as e:
            self.run_main("Refs example/private-app#12", read_token=None)
        self.assertIn("ISSUE_READ_TOKEN is not set", str(e.exception.code))

    def test_server_error_is_not_swallowed(self):
        def boom(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 500, "err", {}, io.BytesIO(b""))
        env = {"FORGEJO_URL": "https://f", "REPO": "a/b", "TOKEN": "job", "PR_BODY": "Closes #1"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(issue_link.urllib.request, "urlopen", boom), \
                self.assertRaises(urllib.error.HTTPError):
            issue_link.main()


if __name__ == "__main__":
    unittest.main()
