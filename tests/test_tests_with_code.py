import importlib.util
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / ".forgejo/scripts/tests-with-code.py"
spec = importlib.util.spec_from_file_location("tests_with_code", SCRIPT)
tests_with_code = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests_with_code)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                          check=True).stdout.strip()


class TestsWithCodeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "t")
        git(self.repo, "config", "core.quotePath", "true")
        self.write("README", "x\n")
        self.base = self.commit()
        self.cwd = pathlib.Path.cwd()
        os.chdir(self.repo)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def write(self, path, text, mode=0o644):
        p = pathlib.Path(self.repo, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        p.chmod(mode)

    def commit(self):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "c")
        return git(self.repo, "rev-parse", "HEAD")

    def run_main(self, head, body=""):
        with mock.patch.dict(os.environ, {"PR_BODY": body}):
            tests_with_code.main(self.base, head)

    def assert_needs_tests(self, path):
        with self.assertRaises(SystemExit) as e:
            self.run_main(self.commit())
        self.assertIn(f"Code changed without tests:\n  {path}\n", str(e.exception.code))

    def test_source_file_needs_a_test(self):
        self.write("app.py", "x = 1\n")
        self.assert_needs_tests("app.py")
        self.write("tests/test_app.py", "x = 1\n")
        self.run_main(self.commit())

    def test_extensionless_executable_needs_a_test(self):
        self.write("launch tool", "#!/bin/sh\n", 0o755)
        self.assert_needs_tests("launch tool")

    def test_zsh_needs_a_test(self):
        self.write("setup.zsh", "true\n")
        self.assert_needs_tests("setup.zsh")

    def test_path_git_quotes_needs_a_test(self):
        self.write("caf\u00e9.py", "x = 1\n")
        self.assert_needs_tests("caf\u00e9.py")

    def test_dropping_the_executable_bit_does_not_exempt_the_change(self):
        self.write("launch", "#!/bin/sh\n", 0o755)
        self.base = self.commit()
        self.write("launch", "#!/bin/sh\necho changed\n", 0o644)
        self.assert_needs_tests("launch")

    def test_symlink_replaced_by_an_executable_needs_a_test(self):
        link = pathlib.Path(self.repo, "launch")
        link.symlink_to("README")
        self.base = self.commit()
        link.unlink()
        self.write("launch", "#!/bin/sh\n", 0o755)
        self.assert_needs_tests("launch")

    def test_type_change_of_a_test_path_is_not_a_test(self):
        link = pathlib.Path(self.repo, "tests/data")
        link.parent.mkdir()
        link.symlink_to("../README")
        self.base = self.commit()
        link.unlink()
        self.write("tests/data", "x\n")
        self.write("app.py", "x = 1\n")
        self.assert_needs_tests("app.py")

    def test_rename_is_judged_by_its_new_path(self):
        self.write("notes.txt", "".join(f"line {i}\n" for i in range(50)))
        self.base = self.commit()
        git(self.repo, "mv", "notes.txt", "app.py")
        self.assert_needs_tests("app.py")

    def test_plain_file_and_ci_tooling_do_not(self):
        self.write("notes", "x\n")
        self.write(".forgejo/scripts/check", "#!/bin/sh\n", 0o755)
        self.run_main(self.commit())

    def test_reason_passes_and_an_empty_one_does_not(self):
        self.write("app.py", "x = 1\n")
        head = self.commit()
        self.run_main(head, body="No tests: generated\n")
        with self.assertRaises(SystemExit):
            self.run_main(head, body="No tests:\n")


if __name__ == "__main__":
    unittest.main()
