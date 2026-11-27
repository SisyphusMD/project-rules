"""The shared workflows and scripts name no git host or service of one instance (#136).

Every value that differs between git hosts lives in the owner's `.project-rules` manifest, so the
same files run unchanged on each host that mirrors this repo.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# The house hosts, and in-cluster service names, which only resolve on one instance's runners.
HOSTS = re.compile(r"(?i)[\w.-]*\b(?:bryantserver|humblepixels)\.(?:com|lan|local)\b|[\w.-]+\.svc\.cluster\.local")
SCANNED = sorted(p for folder in (".forgejo", "tools") for p in (ROOT / folder).rglob("*") if p.is_file())


def test_the_scan_sees_the_workflows_and_scripts() -> None:
    names = {p.relative_to(ROOT).as_posix() for p in SCANNED}
    assert {".forgejo/workflows/review.yml", ".forgejo/scripts/ai-review.py", "tools/vendor.py"} <= names


@pytest.mark.parametrize("path", SCANNED, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_instance_host_is_named(path: Path) -> None:
    found = HOSTS.findall(path.read_text(errors="replace"))
    assert not found, f"{path.relative_to(ROOT)} names {sorted(set(found))}: put it in the owner manifest"


# Made-up names of each shape the pattern must catch; public text never names a real internal host.
@pytest.mark.parametrize("text", [
    "https://mirror.lan.bryantserver.com/simple/",
    "bot@noreply.bryantserver.com",
    "http://llm.ns.svc.cluster.local:8080/v1",
    "https://git.humblepixels.com/acme/app",
])
def test_the_pattern_catches_each_kind_of_instance_host(text: str) -> None:
    assert HOSTS.search(text)
