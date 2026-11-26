"""Who can start an AI review: the job's own `if:` evaluated against Forgejo-shaped payloads (#116)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

# The file repos call (#78): there github.event_name reads workflow_call for every event.
WORKFLOW = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows" / "review.yml"
REF = re.compile(r"github(?:\.[A-Za-z_]+)+")
LITERAL = re.compile(r"'[^']*'")


def evaluate(condition: str, github: dict) -> bool:
    """Evaluate the subset of Actions expressions the job uses: refs, quoted literals, ==, !=, &&, ||."""

    # A missing path reads as null, as on the runner: the pull_request_target path already reads
    # github.event.comment, which that payload lacks.
    def lookup(path: str):
        value = github
        for part in path.split(".")[1:]:
            value = value.get(part) if isinstance(value, dict) else None
        return value

    names: dict[str, object] = {}

    def bind(value) -> str:
        names[f"v{len(names)}"] = value
        return f"v{len(names) - 1}"

    text = LITERAL.sub(lambda m: bind(m.group(0)[1:-1]), condition)
    text = REF.sub(lambda m: bind(lookup(m.group(0))), text)
    text = text.replace("&&", " and ").replace("||", " or ")
    if not re.fullmatch(r"[\sv\d()=!andor]*", text):
        raise ValueError(f"unsupported expression: {condition}")
    # The fullmatch above leaves only bound names and operators to evaluate.
    return bool(eval(text, {"__builtins__": {}}, names))


def job_condition(path: Path = WORKFLOW) -> str:
    spec = yaml.safe_load(path.read_text())["jobs"]["review"]
    return " ".join(str(spec["if"]).split())


def comment(by: str, *, can_push: bool, pr_author: str = "alice", on_pr: bool = True) -> dict:
    # Forgejo's comment payload carries the commenter's own permission in repository.permissions
    # (services/actions/notifier.go notifyIssueCommentChange).
    return {
        "event_name": "issue_comment",
        "event": {
            "issue": {"pull_request": {"merged": False} if on_pr else None, "user": {"login": pr_author}},
            "comment": {"user": {"login": by}},
            "repository": {"permissions": {"admin": False, "push": can_push, "pull": True}},
        },
    }


def called(payload: dict) -> dict:
    return {**payload, "event_name": "workflow_call"}


PR_EVENT = {"event_name": "pull_request_target", "event": {"pull_request": {"number": 9}}}


@pytest.mark.parametrize(
    ("payload", "runs"),
    [
        pytest.param(PR_EVENT, True, id="pr-event"),
        pytest.param(comment("cody", can_push=True), True, id="maintainer-reply"),
        pytest.param(comment("alice", can_push=False), True, id="pr-author-reply"),
        pytest.param(comment("stranger", can_push=False), False, id="outside-comment"),
        pytest.param(comment("forgejo-actions", can_push=True), False, id="reviewer-own-comment"),
        pytest.param(comment("cody", can_push=True, on_pr=False), False, id="issue-not-pr"),
    ],
)
def test_who_starts_a_review(payload: dict, runs: bool) -> None:
    assert evaluate(job_condition(), called(payload)) is runs


def test_the_called_job_does_not_read_the_event_name() -> None:
    # It always reads workflow_call there, so a rule built on it would never see a PR event.
    assert "event_name" not in job_condition()


@pytest.mark.parametrize("by, runs", [("stranger", False), ("alice", True)])
def test_a_payload_without_permissions_falls_back_to_the_pr_author(by: str, runs: bool) -> None:
    payload = comment(by, can_push=True)
    del payload["event"]["repository"]
    assert evaluate(job_condition(), called(payload)) is runs


def test_the_evaluator_reads_the_old_ungated_condition_as_open(tmp_path: Path) -> None:
    old = tmp_path / "ai-review.yml"
    old.write_text(
        yaml.safe_dump(
            {
                "jobs": {
                    "review": {
                        "if": "github.event_name == 'pull_request_target' || (github.event.issue.pull_request"
                        " && github.event.comment.user.login != 'forgejo-actions')"
                    }
                }
            }
        )
    )
    assert evaluate(job_condition(old), comment("stranger", can_push=False)) is True
