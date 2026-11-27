"""Every gate job runs its script from the one fetched copy of project-rules main."""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".forgejo" / "workflows"
FETCH = "Fetch the gate scripts"
MANIFEST = "Read the owner's manifest"
GATE_JOBS = {
    ("gate.yml", "issue-link"): "issue-link",
    ("gate.yml", "tests-with-code"): "tests-with-code",
    ("gate.yml", "diff-size"): "diff-size",
    ("review.yml", "review"): "ai-review",
}


def steps(workflow: str, job: str) -> list[dict]:
    return yaml.safe_load((WORKFLOWS / workflow).read_text())["jobs"][job]["steps"]


def fetch_step(workflow: str, job: str) -> dict:
    return next(step for step in steps(workflow, job) if step.get("name") == FETCH)


@pytest.mark.parametrize(("where", "script"), GATE_JOBS.items())
def test_gate_job_runs_only_the_fetched_script(where: tuple[str, str], script: str) -> None:
    found = steps(*where)
    names = [step.get("name") for step in found]
    checkouts = [i for i, step in enumerate(found) if "checkout" in step.get("uses", "")]
    assert all(names.index(FETCH) < i for i in checkouts), "fetched before the PR is checked out"
    # The manifest step's reader is the fetched copy too; test_owner_manifest.py covers it.
    runs = "\n".join(step.get("run", "") for step in found if step.get("name") != MANIFEST)
    used = re.findall(r"(\S*\.forgejo/scripts/\S+)", runs)
    assert used == [f"/tmp/gate/.forgejo/scripts/{script}.py"]


@pytest.mark.parametrize(("where", "script"), GATE_JOBS.items())
def test_the_job_fails_when_its_fetched_script_does(
    where: tuple[str, str], script: str, tmp_path: Path
) -> None:
    gate = tmp_path / "gate/.forgejo/scripts"
    gate.mkdir(parents=True)
    (gate / f"{script}.py").write_text("raise SystemExit(7)\n")
    subprocess.run(["git", "init", "-q", tmp_path], check=True)
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "-C", tmp_path, *identity, "commit", "-q", "--allow-empty", "-m", "c"],
                   check=True)
    step = steps(*where)[-1]
    env = {**os.environ, "BASE_SHA": "HEAD", "HEAD_SHA": "HEAD", "TOKEN": "x"}
    run = step["run"].replace("/tmp/gate", str(tmp_path / "gate"))
    result = subprocess.run(["bash", "-e", "-c", run], cwd=tmp_path, env=env,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 7, result.stderr


CANNOT_START = "Fail the check when the review cannot start"


@pytest.mark.parametrize("state", ["open", "closed"])
def test_a_rereview_replaces_the_old_pass_before_anything_can_fail(state: str) -> None:
    found = steps("review.yml", "review")
    hold = found[0]
    assert hold["name"] == "Hold the check until this review answers"
    assert found[1]["name"] == FETCH
    expected = [("/r/statuses/abc", "pending", "AI review", "token t", "Starting")]
    assert post_status(hold, state) == (expected if state == "open" else [])


@pytest.mark.parametrize("state", ["open", "closed"])
def test_a_failed_fetch_or_manifest_read_turns_the_held_check_into_an_error(state: str) -> None:
    found = steps("review.yml", "review")
    names = [step.get("name") for step in found]
    step = found[names.index(CANNOT_START)]
    # Right after the reads and before anything the review script does, which posts its own.
    assert names.index(CANNOT_START) == names.index(MANIFEST) + 1 > names.index(FETCH)
    assert step["if"] == "failure()"
    assert step["run"] == found[0]["run"]
    description = "Could not fetch the gate scripts or read the owner's .project-rules manifest; see the job log"
    expected = [("/r/statuses/abc", "error", "AI review", "token t", description)]
    assert post_status(step, state) == (expected if state == "open" else [])


def post_status(step: dict, state: str) -> list[tuple[str, ...]]:
    posted = []

    class Handler(BaseHTTPRequestHandler):
        def reply(self, body: dict) -> None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

        def do_GET(self) -> None:
            assert self.path == "/r/pulls/9"
            self.reply({"state": state, "head": {"sha": "abc"}})

        def do_POST(self) -> None:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            posted.append((self.path, body["state"], body["context"], self.headers["Authorization"],
                           body["description"]))
            self.reply({})

        def log_message(self, *args: object) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        subprocess.run(
            ["bash", "-e", "-c", step["run"]], check=True,
            env={**os.environ, "API": f"http://127.0.0.1:{server.server_port}/r", "PR": "9", "TOKEN": "t",
                 "STATE": step["env"]["STATE"], "DESCRIPTION": step["env"]["DESCRIPTION"]},
        )
    finally:
        server.shutdown()
        server.server_close()
    return posted


def test_the_archive_job_runs_only_the_fetched_script() -> None:
    # Not in GATE_JOBS: its last step clones and pushes, so it cannot be run here.
    run = "\n".join(step.get("run", "") for step in steps("archive.yml", "archive")
                    if step.get("name") != MANIFEST)
    assert re.findall(r"(\S*\.forgejo/scripts/\S+)", run) == ["/tmp/gate/.forgejo/scripts/issue-archive.py"]
    assert "python3 -I /tmp/gate/.forgejo/scripts/issue-archive.py archive\n" in run
    assert "git -C archive add -A" in run


def test_every_copy_of_the_fetch_step_is_the_one_the_tests_workflow_proves() -> None:
    proven = fetch_step("tests.yml", "gate-fetch")
    for where in [*GATE_JOBS, ("archive.yml", "archive")]:
        assert fetch_step(*where) == proven, where


def fetch(tmp_path: Path, url: str) -> subprocess.CompletedProcess[str]:
    run = fetch_step("tests.yml", "gate-fetch")["run"]
    assert run.count("/tmp/gate") == 2
    # macOS has no timeout(1); the runner does.
    shim = tmp_path / "bin/timeout"
    shim.parent.mkdir()
    shim.write_text('#!/bin/sh\nshift\nexec "$@"\n')
    shim.chmod(0o755)
    return subprocess.run(
        ["bash", "-c", run.replace("/tmp/gate", str(tmp_path / "gate"))],
        cwd=tmp_path,
        env={**os.environ, "PATH": f"{shim.parent}:{os.environ['PATH']}", "FORGEJO_URL": url},
        capture_output=True, text=True, check=False,
    )


def test_fetch_takes_main_and_names_its_commit(tmp_path: Path) -> None:
    source = tmp_path / "forge/SisyphusMD/project-rules.git"
    source.mkdir(parents=True)

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", source, "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            capture_output=True, text=True, check=True,
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    (source / "which").write_text("main")
    git("add", "which")
    git("commit", "-qm", "main")
    main = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "other")
    (source / "which").write_text("other")
    git("commit", "-qam", "other")

    result = fetch(tmp_path, f"file://{tmp_path}/forge")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"gate scripts: project-rules {main}"
    assert (tmp_path / "gate/which").read_text() == "main"


def test_fetch_fails_when_the_repo_cannot_be_read(tmp_path: Path) -> None:
    result = fetch(tmp_path, f"file://{tmp_path}/missing")
    assert result.returncode != 0
    assert "missing/SisyphusMD/project-rules.git" in result.stderr
