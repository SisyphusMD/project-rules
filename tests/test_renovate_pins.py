"""Every pinned version in the workflows and shared scripts is one Renovate can see.

Renovate here only reads what .renovaterc.json describes, and a pin it cannot see is never bumped
and never reported, so these checks are the only thing that notices one.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".forgejo/workflows").glob("*.yml"))
CONFIG = json.loads((ROOT / ".renovaterc.json").read_text())


def python_regex(js):
    return re.compile(js.replace("(?<", "(?P<"))


def managed(path):
    rel = path.relative_to(ROOT).as_posix()
    return [python_regex(m["matchStrings"][0]) for m in CONFIG["customManagers"]
            if any(re.search(p.strip("/"), rel) for p in m["managerFilePatterns"])]


class RenovatePinsTest(unittest.TestCase):
    def test_sha_pinned_actions_name_their_version(self):
        for wf in WORKFLOWS:
            for n, line in enumerate(wf.read_text().splitlines(), 1):
                if re.search(r"uses: \S+@[0-9a-f]{40}", line):
                    self.assertRegex(line, r"@[0-9a-f]{40} # v\d", f"{wf.name}:{n}")

    def test_setup_python_pins_an_exact_interpreter(self):
        for wf in WORKFLOWS:
            for n, line in enumerate(wf.read_text().splitlines(), 1):
                if "python-version:" in line:
                    self.assertRegex(line, r'python-version: "\d+\.\d+\.\d+"', f"{wf.name}:{n}")

    def test_every_version_pin_carries_a_matching_annotation(self):
        files = [*WORKFLOWS, *sorted((ROOT / "shared/packaging").glob("*.sh"))]
        pin = re.compile(r'^\s*[A-Z][A-Z0-9_]*[:=] *"?v?\d+\.\d+|==\d')
        for f in files:
            lines = f.read_text().splitlines()
            matched = set()
            for rx in managed(f):
                for m in rx.finditer(f.read_text()):
                    matched.add(f.read_text()[:m.end()].count("\n"))
            for n, line in enumerate(lines):
                if pin.search(line) and "SHA256" not in line and "$" not in line.split("==")[-1]:
                    self.assertIn(n, matched, f"{f.relative_to(ROOT)}:{n + 1} has no annotation "
                                  "Renovate reads")


if __name__ == "__main__":
    unittest.main()
