"""pyproject.toml, CHANGELOG.md and the release tag name one version.

Consumers resolve a release by its tag, so a version written by hand anywhere else drifts unless
something compares it. RELEASE_TAG is set by the tag's Tests run.
"""
import os
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def project_version():
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


def newest_changelog_release():
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", (ROOT / "CHANGELOG.md").read_text(), re.M)
    return m.group(1) if m else None


class ReleaseMetadataTest(unittest.TestCase):
    def test_pyproject_matches_the_newest_changelog_release(self):
        self.assertEqual(project_version(), newest_changelog_release())

    def test_changelog_keeps_one_unreleased_section(self):
        self.assertEqual(len(re.findall(r"^## \[Unreleased\]$",
                                        (ROOT / "CHANGELOG.md").read_text(), re.M)), 1)

    @unittest.skipUnless(os.environ.get("RELEASE_TAG"), "only on a tag")
    def test_tag_matches_pyproject(self):
        self.assertEqual(os.environ["RELEASE_TAG"], f"v{project_version()}")


if __name__ == "__main__":
    unittest.main()
