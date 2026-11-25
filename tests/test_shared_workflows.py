"""The workflows repos call instead of copying (#78) hold exactly the jobs the gate runs."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows"
SHARED = {"gate.yml": "ci.yml", "gate-lint.yml": "ci.yml", "review.yml": "ai-review.yml"}


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


def without_guard(jobs: dict) -> dict:
    return {name: {**job, "steps": [s for s in job["steps"] if s.get("name") != GUARD]}
            for name, job in jobs.items()}


def test_the_gate_files_hold_every_ci_job_once() -> None:
    gate, lint = load("gate.yml")["jobs"], load("gate-lint.yml")["jobs"]
    assert not set(gate) & set(lint)
    # The same jobs as the copied ci.yml, plus the fork guard below.
    assert without_guard({**gate, **lint}) == load("ci.yml")["jobs"]


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


def test_the_review_job_matches_the_copied_one_but_for_its_trigger_rule() -> None:
    shared, copied = load("review.yml")["jobs"], load("ai-review.yml")["jobs"]
    assert set(shared) == set(copied) == {"review"}
    shared, copied = dict(shared["review"]), dict(copied["review"])
    # The rule differs only in how it spots a PR event: github.event_name reads workflow_call in a
    # called file, so it tests for the pull_request payload instead.
    assert shared.pop("if").replace("github.event.pull_request ||", "github.event_name == 'pull_request_target' ||") \
        == copied.pop("if")
    assert shared == copied
