"""A workflow that repos copy says where its canonical copy is."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# tests.yml and owners.yml are this repo's own; repos call gate.yml, gate-lint.yml and review.yml from here (#78);
# docs/adopting.md has every other workflow copied.
NOT_COPIED = {"tests.yml", "owners.yml", "gate.yml", "gate-lint.yml", "review.yml"}
COPIED = sorted(
    path.relative_to(ROOT).as_posix()
    for folder in (".forgejo/workflows", ".github/workflows")
    for path in (ROOT / folder).glob("*.y*ml")
    if path.name not in NOT_COPIED
)


def test_discovery_finds_the_copied_workflows() -> None:
    assert {".forgejo/workflows/ci.yml", ".github/workflows/mirror-lockdown.yml"} <= set(COPIED)


@pytest.mark.parametrize("path", COPIED)
def test_copied_workflow_names_its_source(path: str) -> None:
    header = []
    for line in (ROOT / path).read_text().splitlines():
        if not line.startswith("#"):
            break
        header.append(line.lstrip("# "))
    assert "Canonical copy: SisyphusMD/project-rules; repos get a copy." in " ".join(header), path
