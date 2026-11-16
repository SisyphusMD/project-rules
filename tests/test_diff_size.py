import importlib.util
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / ".forgejo/scripts/diff-size.py"
spec = importlib.util.spec_from_file_location("diff_size", SCRIPT)
diff_size = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diff_size)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                          check=True).stdout.strip()


class DiffSizeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "t")
        self.write("README", "x\n")
        self.base = self.commit()
        self.cwd = os.getcwd()
        os.chdir(self.repo)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def write(self, path, text):
        p = pathlib.Path(self.repo, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "c")
        return git(self.repo, "rev-parse", "HEAD")

    def lines(self, n):
        return "".join(f"line {i}\n" for i in range(n))

    def run_main(self, head, body=""):
        with mock.patch.dict(os.environ, {"PR_BODY": body, "DIFF_LIMIT": "400"}):
            diff_size.main(self.base, head)

    def test_counts_code_but_not_tests_or_lockfiles(self):
        self.write("app/main.py", self.lines(10))
        self.write("tests/test_main.py", self.lines(500))
        self.write("web/package-lock.json", self.lines(500))
        head = self.commit()
        self.assertEqual(diff_size.changed_lines(self.base, head), 10)

    def test_counts_deleted_lines(self):
        self.write("app/main.py", self.lines(30))
        self.base = self.commit()
        os.remove(pathlib.Path(self.repo, "app/main.py"))
        head = self.commit()
        self.assertEqual(diff_size.changed_lines(self.base, head), 30)

    def test_pure_rename_counts_nothing_but_rename_into_tests_counts(self):
        self.write("app/main.py", self.lines(50))
        self.base = self.commit()
        git(self.repo, "mv", "app/main.py", "app/core.py")
        renamed = self.commit()
        self.assertEqual(diff_size.changed_lines(self.base, renamed), 0)
        pathlib.Path(self.repo, "tests").mkdir()
        git(self.repo, "mv", "app/core.py", "tests/core.py")
        pathlib.Path(self.repo, "tests/core.py").write_text(self.lines(50) + "extra\n")
        moved = self.commit()
        self.assertEqual(diff_size.changed_lines(renamed, moved), 1)

    def test_binary_files_count_zero(self):
        pathlib.Path(self.repo, "logo.png").write_bytes(bytes(range(256)) * 10)
        head = self.commit()
        self.assertEqual(diff_size.changed_lines(self.base, head), 0)

    def test_at_limit_passes(self):
        self.write("app/main.py", self.lines(400))
        self.run_main(self.commit())

    def test_over_limit_fails_without_reason(self):
        self.write("app/main.py", self.lines(401))
        head = self.commit()
        with self.assertRaises(SystemExit) as e:
            self.run_main(head)
        self.assertIn("401 changed lines", str(e.exception.code))

    def test_over_limit_passes_with_reason(self):
        self.write("app/main.py", self.lines(401))
        head = self.commit()
        self.run_main(head, body="Closes #1\n\nLarge diff: generated client from the API schema\n")

    def test_empty_reason_does_not_count(self):
        self.write("app/main.py", self.lines(401))
        head = self.commit()
        with self.assertRaises(SystemExit):
            self.run_main(head, body="Large diff:\n")


if __name__ == "__main__":
    unittest.main()
