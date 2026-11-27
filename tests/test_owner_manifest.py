"""The shared jobs take every host-specific value from the owner's manifest, never their own text (#136)."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".forgejo" / "workflows"
FETCH = "Fetch the gate scripts"
READ = "Read the owner's manifest"
READERS = [("gate-lint.yml", "lint"), ("gate-lint.yml", "secrets"), ("review.yml", "review"),
           ("issue-archive.yml", "archive")]
GOOD = {
    "visibility": "private",
    "mirrors": ["https://backup.example"],
    "decided_by": "Cody",
    "bot_email": "issue-archive+acme@noreply.example.com",
    "llm_url": "http://llm.example:8080/v1/chat/completions",
    "ai_review": "required",
    "package_index": "https://mirror.example/pypi.org/simple/",
    "release_mirror": "https://mirror.example/github.com",
}


def steps(workflow: str, job: str) -> list[dict]:
    return yaml.safe_load((WORKFLOWS / workflow).read_text())["jobs"][job]["steps"]


def step(workflow: str, job: str, name: str) -> dict:
    return next(s for s in steps(workflow, job) if s.get("name") == name)


def proven() -> dict:
    return step("owners.yml", "manifests", READ)


@pytest.mark.parametrize("where", READERS)
def test_every_copy_of_the_read_step_is_the_one_the_tests_workflow_proves(where: tuple[str, str]) -> None:
    assert step(*where, READ) == proven()


@pytest.mark.parametrize("where", READERS)
def test_the_manifest_is_read_after_the_fetch_and_before_any_checkout(where: tuple[str, str]) -> None:
    found = steps(*where)
    names = [s.get("name") for s in found]
    checkouts = [i for i, s in enumerate(found) if "checkout" in s.get("uses", "")]
    assert names.index(FETCH) < names.index(READ)
    assert all(names.index(READ) < i for i in checkouts)


@pytest.mark.parametrize(("where", "name", "variable"), [
    (("gate-lint.yml", "lint"), "Install linters", "PACKAGE_INDEX"),
    (("gate-lint.yml", "secrets"), "gitleaks over the PR head's history", "RELEASE_MIRROR"),
    (("issue-archive.yml", "archive"), "Export to the issue-archive branch", "BOT_EMAIL"),
])
def test_a_job_takes_its_host_value_from_the_manifest_or_fails(where: tuple[str, str], name: str,
                                                               variable: str) -> None:
    run = step(*where, name)["run"]
    assert f"${{{variable}:?from the owner manifest}}" in run
    assert "https://" not in run


def test_the_review_gets_its_model_endpoint_only_from_the_manifest() -> None:
    env = step("review.yml", "review", "Review the PR")["env"]
    assert not {"LLM_URL", "AI_REVIEW", "AI_REVIEW_EXEMPT"} & set(env)


def run_read(tmp_path: Path, manifest: object | None,
             token: str = "t") -> tuple[subprocess.CompletedProcess[str], str]:
    host = tmp_path / "host"
    if manifest is not None:
        source = host / "acme/.project-rules.git"
        source.mkdir(parents=True)
        (source / "env.json").write_text(manifest if isinstance(manifest, str) else json.dumps(manifest))
        git = ["git", "-C", source, "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
        subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
        subprocess.run([*git, "add", "env.json"], check=True)
        subprocess.run([*git, "commit", "-qm", "m"], check=True)
    # macOS has no timeout(1) and its base64 has no -w; the runner has both. A file:// clone
    # ignores the header anyway.
    shim = tmp_path / "bin/timeout"
    shim.parent.mkdir()
    shim.write_text('#!/bin/sh\nshift\nexec "$@"\n')
    (shim.parent / "base64").write_text("#!/bin/sh\ncat >/dev/null\necho eDp0\n")
    for tool in shim.parent.iterdir():
        tool.chmod(0o755)
    run = proven()["run"].replace("/tmp/gate", str(ROOT)).replace("/tmp/manifest", str(tmp_path / "m"))
    github_env = tmp_path / "github_env"
    github_env.write_text("")
    result = subprocess.run(
        ["bash", "-c", run], capture_output=True, text=True, check=False,
        env={**os.environ, "PATH": f"{shim.parent}:{os.environ['PATH']}", "FORGEJO_URL": f"file://{host}",
             "OWNER": "acme", "TOKEN": token, "GITHUB_ENV": str(github_env)},
    )
    return result, github_env.read_text()


def test_without_the_owner_token_the_read_fails_before_trying(tmp_path: Path) -> None:
    result, env = run_read(tmp_path, GOOD, token="")
    assert result.returncode != 0
    assert "No PROJECT_RULES_TOKEN" in result.stderr
    assert env == ""


@pytest.mark.parametrize("where", [*READERS, ("owners.yml", "manifests")])
def test_the_manifest_is_read_with_the_owner_token_not_the_job_token(where: tuple[str, str]) -> None:
    # The manifest is private and the job token cannot read another repo, so it must be the
    # bot token the owner keeps as an Actions secret.
    assert step(*where, READ)["env"]["TOKEN"] == "${{ secrets.PROJECT_RULES_TOKEN }}"


def test_the_owners_checks_use_the_owner_token_too() -> None:
    owners = yaml.safe_load((WORKFLOWS / "owners.yml").read_text())
    for job in owners["jobs"].values():
        for s in job["steps"]:
            if "TOKEN" in s.get("env", {}):
                assert s["env"]["TOKEN"] == "${{ secrets.PROJECT_RULES_TOKEN }}", s.get("name")


def test_the_read_step_hands_the_values_to_later_steps(tmp_path: Path) -> None:
    result, env = run_read(tmp_path, GOOD)
    assert result.returncode == 0, result.stderr
    assert re.fullmatch(r"owner manifest: acme/\.project-rules [0-9a-f]{40}\n", result.stdout)
    assert "PACKAGE_INDEX=https://mirror.example/pypi.org/simple/\n" in env
    assert "AI_REVIEW=required\n" in env


HANDOFF = "The manifest's values reach later steps"
EXEMPT = {**{k: v for k, v in GOOD.items() if k != "llm_url"}, "ai_review": {"exempt": "acme/.project-rules#1"}}


NAMES = ("AI_REVIEW", "AI_REVIEW_EXEMPT", "VISIBILITY", "LLM_URL", "PACKAGE_INDEX", "RELEASE_MIRROR", "BOT_EMAIL")


def run_handoff(tmp_path: Path, env_text: str, runner: dict | None = None) -> subprocess.CompletedProcess[str]:
    """The handoff step after run_read, with env_text as what $GITHUB_ENV delivered."""
    values = dict(line.split("=", 1) for line in env_text.splitlines())
    clean = {k: v for k, v in os.environ.items() if k not in NAMES}
    run = (step("owners.yml", "manifests", HANDOFF)["run"].replace("/tmp/gate", str(ROOT))
           .replace("/tmp/manifest", str(tmp_path / "m")).replace("/tmp/expected", str(tmp_path / "expected")))
    return subprocess.run(["bash", "-c", run], capture_output=True, text=True, check=False,
                          env={**clean, **(runner or {}), **values})


@pytest.mark.parametrize("manifest", [GOOD, EXEMPT], ids=["required", "exempt"])
def test_the_handoff_check_passes_on_what_the_read_step_writes(tmp_path: Path, manifest: dict) -> None:
    result, env = run_read(tmp_path, manifest)
    assert result.returncode == 0, result.stderr
    check = run_handoff(tmp_path, env)
    assert check.returncode == 0, check.stderr
    assert "PACKAGE_INDEX arrived" in check.stdout
    assert "mirror.example" not in check.stdout


@pytest.mark.parametrize("runner", [{}, {"BOT_EMAIL": "someone@else.example"}], ids=["unset", "runner-has-one"])
def test_the_handoff_check_names_a_value_that_did_not_arrive(tmp_path: Path, runner: dict) -> None:
    _, env = run_read(tmp_path, GOOD)
    dropped = "\n".join(line for line in env.splitlines() if not line.startswith("BOT_EMAIL="))
    check = run_handoff(tmp_path, dropped, runner)
    assert check.returncode != 0
    assert "BOT_EMAIL was not handed on by the read step" in check.stderr


def test_a_missing_manifest_fails_the_step_and_says_where_to_put_one(tmp_path: Path) -> None:
    result, env = run_read(tmp_path, None)
    assert result.returncode != 0
    assert result.stderr.strip() == "Cannot read acme/.project-rules: every owner keeps its settings in its env.json."
    assert "file:" not in result.stderr
    assert env == ""


def test_an_invalid_manifest_fails_the_step_and_hands_on_nothing(tmp_path: Path) -> None:
    result, env = run_read(tmp_path, {**GOOD, "package_index": "https://x.example/ --index-url=evil"})
    assert result.returncode != 0
    assert "package_index is not a URL" in result.stderr
    assert env == ""


def test_the_owners_checks_never_run_a_pull_requests_code_with_the_owner_token() -> None:
    # Its token reads every owner's private manifest, so PRs get main's copy (pull_request_target)
    # and the default checkout of main, never the head.
    owners = yaml.safe_load((WORKFLOWS / "owners.yml").read_text())
    assert "pull_request" not in owners[True] and "pull_request_target" in owners[True]
    for job in owners["jobs"].values():
        for s in job["steps"]:
            assert "with" not in s, s
