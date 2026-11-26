"""The workflows repos call instead of copying (#78) hold exactly the jobs the gate runs."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows"
SHARED = ("gate.yml", "gate-lint.yml", "review.yml")


def load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text())


@pytest.mark.parametrize("name", SHARED)
def test_a_shared_workflow_runs_only_when_called(name: str) -> None:
    # PyYAML reads the `on:` key as True.
    assert load(name)[True] == {"workflow_call": None}


@pytest.mark.parametrize("name", SHARED)
def test_a_shared_workflow_sets_no_concurrency(name: str) -> None:
    # Forgejo ignores it in a called file, so a group here would only look like protection.
    assert "concurrency" not in load(name)
    assert all("concurrency" not in job for job in load(name)["jobs"].values())


GUARD = "Refuse a fork's code"
MAIN = "SisyphusMD/project-rules/.forgejo/workflows/{}@main"
TOKEN = {"ISSUE_READ_TOKEN": "${{ secrets.ISSUE_READ_TOKEN }}"}


def test_the_called_jobs_carry_the_required_check_names() -> None:
    names = {name: sorted(job["name"] for job in load(name)["jobs"].values()) for name in SHARED}
    assert names == {"gate.yml": ["Diff size", "Issue link", "Tests with code"],
                     "gate-lint.yml": ["Lint", "Secrets"], "review.yml": ["Review"]}


def test_the_canonical_callers_call_main_and_hand_over_only_the_issue_reader() -> None:
    # Named, never `secrets: inherit`, so main's jobs see no other secret of the calling repo.
    assert load("ci.yml")["jobs"] == {
        "shared-gate": {"uses": MAIN.format("gate.yml"), "secrets": TOKEN},
        "shared-lint": {"uses": MAIN.format("gate-lint.yml")},
    }
    assert load("ai-review.yml")["jobs"] == {
        "shared-review": {"uses": MAIN.format("review.yml"), "secrets": TOKEN}}


def test_the_callers_keep_the_triggers_and_concurrency() -> None:
    ci, review = load("ci.yml"), load("ai-review.yml")
    assert set(ci[True]) == {"pull_request_target"}
    assert set(review[True]) == {"pull_request_target", "issue_comment"}
    assert ci["concurrency"]["cancel-in-progress"] is True
    # A review is never cancelled between saving its findings and its status.
    assert review["concurrency"]["cancel-in-progress"] is False


def test_a_calling_job_never_shares_a_name_with_a_required_check() -> None:
    required = {job["name"].lower() for name in SHARED for job in load(name)["jobs"].values()}
    callers = {job.lower() for name in ("ci.yml", "ai-review.yml") for job in load(name)["jobs"]}
    assert not required & callers


def head_checkouts() -> list[tuple[str, str]]:
    return [(name, job) for name in SHARED for job, spec in load(name)["jobs"].items()
            if any("checkout" in s.get("uses", "") and "head.sha" in str(s.get("with", {}).get("ref"))
                   for s in spec["steps"])]


def test_the_jobs_that_check_out_a_pr_head_are_known() -> None:
    assert head_checkouts() == [("gate.yml", "tests-with-code"), ("gate.yml", "diff-size"),
                                ("gate-lint.yml", "lint"), ("gate-lint.yml", "secrets")]


@pytest.mark.parametrize(("name", "job"), head_checkouts())
def test_a_job_refuses_a_fork_before_it_checks_out_the_head(name: str, job: str) -> None:
    steps = load(name)["jobs"][job]["steps"]
    names = [s.get("name") for s in steps]
    first = next(i for i, s in enumerate(steps) if "checkout" in s.get("uses", ""))
    assert GUARD in names and names.index(GUARD) < first


@pytest.mark.parametrize(
    ("head", "refused"),
    [("7", False), ("8", True), ("", False)],
    ids=["same-repo-or-agit", "fork", "no-head-repo"],
)
def test_the_fork_guard_applies_checkouts_rule(head: str, refused: bool) -> None:
    # checkout v7.0.1 refuses only when the head repo's id is known and differs from the base's.
    step = next(s for s in load("gate.yml")["jobs"]["diff-size"]["steps"] if s.get("name") == GUARD)
    result = subprocess.run(["bash", "-e", "-c", step["run"]], capture_output=True, text=True,
                            env={**os.environ, "BASE_ID": "7", "HEAD_ID": head}, check=False)
    assert (result.returncode != 0) is refused, result.stderr
