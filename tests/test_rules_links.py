"""RULES.md is read in every repo's AI review, so its links must work from anywhere.

A relative link resolves to nothing outside this repo; an absolute link to this repository is checked here instead, against the files it names. RULES.md links to
no headings, so fragments are not checked.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = re.sub(r"^```.*?^```", "", (ROOT / "RULES.md").read_text(), flags=re.M | re.S)
REPO = "https://forgejo.bryantserver.com/SisyphusMD/project-rules"
OWN = REPO + "/src/branch/main/"
_INLINE = re.compile(r"\]\(<?([^)\s>]+)>?(?:\s+[^)]*)?\)")
_AUTOLINK = re.compile(r"<([^>\s]+)>")
_DEFINED = re.compile(r"(?m)^\[[^\]]+\]:\s*(\S+)")
_SCHEME = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:")


def targets():
    autolinks = [t for t in _AUTOLINK.findall(TEXT) if "/" in t or ":" in t]
    return _INLINE.findall(TEXT) + _DEFINED.findall(TEXT) + autolinks


class RulesLinksTest(unittest.TestCase):
    def test_no_relative_links(self):
        relative = [t for t in targets() if not (_SCHEME.match(t) or t.startswith("#"))]
        self.assertEqual(relative, [])

    def test_links_to_this_repo_use_the_forgejo_main_url(self):
        # The GitHub copy is a mirror and a tag or commit URL goes stale; the repo's own pages
        # (home, issues) and its files on main are the links that stay right.
        stale = ("/src/tag/", "/src/commit/", "/raw/", "/media/")
        stray = [
            t
            for t in targets()
            if "project-rules" in t
            and (not (t == REPO or t.startswith(REPO + "/")) or any(s in t for s in stale))
        ]
        self.assertEqual(stray, [])

    def test_links_into_this_repo_name_files_that_exist(self):
        own = [t[len(OWN) :].split("#")[0] for t in targets() if t.startswith(OWN)]
        self.assertTrue(own)
        for path in own:
            self.assertTrue((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
