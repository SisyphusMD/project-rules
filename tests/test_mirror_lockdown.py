"""The mirror-lockdown workflow runs with a write token on pull requests from strangers, and every
repo copies it, so the properties that keep it safe are pinned here."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / ".github" / "workflows" / "mirror-lockdown.yml").read_text()
GUARD = "github.server_url == 'https://github.com' && github.repository_owner == 'SisyphusMD'"


def jobs():
    """Each job's own lines (4-space keys), by name; comments dropped. CI has no YAML parser."""
    body = TEXT.split("\njobs:\n", 1)[1]
    found = {}
    for block in re.split(r"(?m)^(?=  [A-Za-z0-9_-]+:\s*$)", body):
        if block.strip():
            name = block.split(":", 1)[0].strip()
            found[name] = [ln for ln in block.splitlines()[1:] if not ln.lstrip().startswith("#")]
    return found


class MirrorLockdownTest(unittest.TestCase):
    def test_every_job_is_guarded_to_the_github_mirror(self):
        # Forgejo runs .github/workflows in a repo without .forgejo/workflows, where this would
        # close the real pull requests; a fork with Actions on would close its own.
        self.assertEqual(list(jobs()), ["lockdown"])
        for name, lines in jobs().items():
            conditions = [ln.strip() for ln in lines if re.match(r"    if:", ln)]
            self.assertEqual(conditions, [f"if: {GUARD}"], name)

    def test_old_pull_requests_are_left_alone(self):
        self.assertRegex(TEXT, r'(?m)^\s+exclude-pr-created-before: "\d{4}-\d\d-\d\dT')

    def test_token_is_scoped_to_pull_requests(self):
        self.assertRegex(TEXT, r"(?m)^permissions: \{\}$")
        job = re.findall(r"(?m)^    permissions:\n((?:      .+\n)+)", TEXT)
        self.assertEqual(job, ["      pull-requests: write\n"])

    def test_runs_no_code_from_the_pull_request(self):
        self.assertNotIn("actions/checkout", TEXT)
        self.assertNotIn("run:", TEXT)

    def test_every_action_is_pinned_by_sha(self):
        uses = re.findall(r"uses:\s*(\S+)", TEXT)
        self.assertTrue(uses)
        for use in uses:
            self.assertRegex(use, r"@[0-9a-f]{40}$", use)


if __name__ == "__main__":
    unittest.main()
