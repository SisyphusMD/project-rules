import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/capability-diff.py"
spec = importlib.util.spec_from_file_location("capability_diff", SCRIPT)
capability_diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capability_diff)


class IssueTemplatePresenceTest(unittest.TestCase):
    def check(self, path):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
            if path:
                (repo / path).parent.mkdir(parents=True)
                (repo / path).write_text("---\nname: Bug\n---\n")
            return capability_diff.corpus(repo, "issue_templates")

    def test_forgejo_path_counts(self):
        self.assertEqual(self.check(".forgejo/issue_template/bug.md"), "present")

    def test_github_path_counts(self):
        self.assertEqual(self.check(".github/ISSUE_TEMPLATE/bug.yml"), "present")

    def test_absent(self):
        self.assertEqual(self.check(None), "")


if __name__ == "__main__":
    unittest.main()
