"""Use a Forgejo response double to exercise the release qualification contract."""

import json
import runpy
from pathlib import Path

import pytest

VERIFY = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "shared/packaging/verify-release-qualification.py"),
)["verify"]
SERVER = "https://forge.example.test"
REPO = "Owner/Repo"
CANDIDATE = "a" * 40
BASE = "b" * 40
URL = f"{SERVER}/{REPO}/actions/runs/42"
JOB = "Open the qualified release PR"
WORKFLOW = "release.yml"


@pytest.fixture
def responses():
    return {
        f"/commits/{CANDIDATE}/status?limit=50": {"statuses": [{
            "context": "Release / Qualified candidate", "status": "success", "target_url": URL,
        }]},
        "/actions/runs?page=1&limit=1&run_number=42": {"workflow_runs": [{
            "html_url": URL, "id": 91, "workflow_id": WORKFLOW, "event_payload": json.dumps({"ref": "refs/heads/main"}),
            "trigger_event": "workflow_dispatch", "status": "success", "commit_sha": BASE,
        }]},
        "/actions/runs/91/jobs": [{"name": JOB, "status": "success", "id": 100}],
        "/actions/jobs/100/logs": f"2026-11-18T01:00:00Z Qualified release commit: {CANDIDATE}\n",
    }


def check(responses):
    VERIFY(SERVER, REPO, CANDIDATE, BASE, WORKFLOW, JOB, lambda path, **_: responses[path])


def test_accepts_exact_successful_dispatch(responses):
    check(responses)


@pytest.mark.parametrize(("key", "value"), [
    ("workflow_id", "another.yml"),
    ("trigger_event", "push"),
    ("status", "failure"),
    ("commit_sha", "c" * 40),
    ("event_payload", json.dumps({"ref": "refs/heads/release/v1.2.3"})),
])
def test_rejects_mismatched_dispatch(responses, key, value):
    responses["/actions/runs?page=1&limit=1&run_number=42"]["workflow_runs"][0][key] = value
    with pytest.raises(ValueError, match="successful Prepare Release dispatch from main"):
        check(responses)


def test_rejects_status_for_another_repository(responses):
    status = responses[f"/commits/{CANDIDATE}/status?limit=50"]["statuses"][0]
    status["target_url"] = URL.replace("/Owner/Repo/", "/Owner/Other/")
    with pytest.raises(ValueError, match="no unique successful"):
        check(responses)


def test_rejects_absent_status(responses):
    responses[f"/commits/{CANDIDATE}/status?limit=50"]["statuses"] = None
    with pytest.raises(ValueError, match="no unique successful"):
        check(responses)


def test_rejects_absent_run(responses):
    responses["/actions/runs?page=1&limit=1&run_number=42"]["workflow_runs"] = None
    with pytest.raises(ValueError, match="run is unavailable"):
        check(responses)


def test_rejects_amended_candidate(responses):
    responses["/actions/jobs/100/logs"] = f"Qualified release commit: {BASE}"
    with pytest.raises(ValueError, match="did not record this candidate"):
        check(responses)


def test_rejects_failed_job(responses):
    responses["/actions/runs/91/jobs"][0]["status"] = "failure"
    with pytest.raises(ValueError, match="job is unavailable"):
        check(responses)
