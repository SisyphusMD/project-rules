"""The repo's own SECURITY.md is the template every repo copies, so the two must not drift."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_security_policy_matches_template():
    own = (ROOT / "SECURITY.md").read_text()
    template = (ROOT / "templates" / "SECURITY.md").read_text()
    assert own == template, "SECURITY.md and templates/SECURITY.md differ; change both together"
