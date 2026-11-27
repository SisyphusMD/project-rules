import importlib.util
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / ".forgejo/scripts" / name
    spec = importlib.util.spec_from_file_location(name[:-3].replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULES = [load(n) for n in ("issue-link.py", "tests-with-code.py", "diff-size.py")]


class PrBodyTest(unittest.TestCase):
    def event(self, payload):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(payload, f)
        self.addCleanup(os.unlink, f.name)
        return f.name

    def body(self, env):
        for module in MODULES:
            with self.subTest(module.__name__), mock.patch.dict(os.environ, env, clear=True):
                yield module.pr_body

    def test_a_body_too_long_for_the_environment_is_read_from_the_event(self):
        # Over Linux's 128 KB limit for one environment string, which made exec fail.
        body = "Closes #1\nNo tests: pins\nLarge diff: notes\n" + "x" * 200_000
        path = self.event({"pull_request": {"body": body}})
        for pr_body in self.body({"GITHUB_EVENT_PATH": path}):
            self.assertEqual(pr_body(), body)

    def test_an_empty_body_is_empty(self):
        for payload in ({"pull_request": {"body": None}}, {"pull_request": {}}):
            for pr_body in self.body({"GITHUB_EVENT_PATH": self.event(payload)}):
                self.assertEqual(pr_body(), "")

    def test_an_unreadable_body_says_why_instead_of_looking_empty(self):
        cases = (({}, "GITHUB_EVENT_PATH is not set"),
                 ({"GITHUB_EVENT_PATH": self.event({"push": {}})}, "not a pull request"))
        for env, message in cases:
            for pr_body in self.body(env):
                with self.assertRaises(SystemExit) as e:
                    pr_body()
                self.assertIn(message, str(e.exception.code))

    def test_pr_body_overrides_the_event(self):
        path = self.event({"pull_request": {"body": "event"}})
        env = {"GITHUB_EVENT_PATH": path, "PR_BODY": "env"}
        for pr_body in self.body(env):
            self.assertEqual(pr_body(), "env")

    def test_the_gate_passes_no_free_text_through_the_environment(self):
        # SHAs, ids and the visibility flag are short; a body, title or message has no length bound.
        jobs = yaml.safe_load((ROOT / ".forgejo/workflows/gate.yml").read_text())["jobs"]
        for job in jobs.values():
            for step in job["steps"]:
                for key, value in (step.get("env") or {}).items():
                    if "github.event" in str(value):
                        self.assertRegex(str(value), r"^\$\{\{ github\.event\.[\w.]+\.(sha|id|private) \}\}$", key)


if __name__ == "__main__":
    unittest.main()
