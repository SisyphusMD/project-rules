"""The owner manifest the gate jobs read: its schema, the env lines they get, drift and visibility (#133)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".forgejo/scripts/manifest.py"
GOOD = {
    "visibility": "private",
    "mirrors": ["https://backup.example"],
    "decided_by": "Cody and Anna",
    "bot_email": "issue-archive+acme@noreply.example.com",
    "llm_url": "http://llm.example:8080/v1/chat/completions",
    "ai_review": "required",
    "package_index": "https://mirror.example/pypi.org/simple/",
    "release_mirror": "https://mirror.example/github.com",
}
EXEMPT = {**{k: v for k, v in GOOD.items() if k != "llm_url"}, "ai_review": {"exempt": "acme/.project-rules#7"}}
SECRET = "https://internal.example/very-private-path"


def run(tmp_path: Path, command: str, *files: object) -> subprocess.CompletedProcess[str]:
    paths = []
    for i, data in enumerate(files):
        path = tmp_path / f"m{i}.json"
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        paths.append(str(path))
    return subprocess.run([sys.executable, "-I", SCRIPT, command, *paths],
                          capture_output=True, text=True, check=False)


def test_a_valid_manifest_becomes_env_lines_for_the_job(tmp_path: Path) -> None:
    result = run(tmp_path, "env", GOOD)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "AI_REVIEW=required", "AI_REVIEW_EXEMPT=",
        "VISIBILITY=private",
        "BOT_EMAIL=issue-archive+acme@noreply.example.com",
        "LLM_URL=http://llm.example:8080/v1/chat/completions",
        "PACKAGE_INDEX=https://mirror.example/pypi.org/simple/",
        "RELEASE_MIRROR=https://mirror.example/github.com",
    ]


def test_an_exempt_owner_names_the_issue_and_needs_no_model(tmp_path: Path) -> None:
    result = run(tmp_path, "env", EXEMPT)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[:2] == ["AI_REVIEW=exempt", "AI_REVIEW_EXEMPT=acme/.project-rules#7"]
    assert not any(line.startswith("LLM_URL=") for line in lines)


@pytest.mark.parametrize(("change", "problem"), [
    ({"llm_url": None}, "missing key 'llm_url'"),
    ({"bot_email": None}, "missing key 'bot_email'"),
    ({"mirrors": None}, "missing key 'mirrors'"),
    ({"visibility": None}, "missing key 'visibility'"),
    ({"decided_by": None}, "missing key 'decided_by'"),
    ({"ai_review": None}, "ai_review must be"),
    ({"ai_review": "off"}, "ai_review must be"),
    ({"ai_review": {"exempt": "a reason"}}, "ai_review must be"),
    ({"ai_review": {"exempt": "acme/k8s#9", "until": "x"}}, "ai_review must be"),
    ({"ai_review": {"exempt": 976}}, "ai_review must be"),
    ({"ai_review": {"exempt": "acme/k8s#0"}}, "ai_review must be"),
    ({"ai_review": {"exempt": "acme/..#1"}}, "ai_review must be"),
    ({"ai_review": {"exempt": "../k8s#1"}}, "ai_review must be"),
    ({"mirror_url": "https://backup.example"}, "unknown key 'mirror_url'"),
    ({"visibility": "internal"}, 'visibility must be "public" or "private"'),
    ({"mirrors": "https://backup.example"}, "mirrors must be a list of distinct URLs"),
    ({"mirrors": []}, "mirrors must be a list of distinct URLs"),
    ({"mirrors": ["https://a.example", "https://a.example"]}, "mirrors must be a list of distinct URLs"),
    ({"mirrors": ["https://a.example", "ftp://b.example"]}, "mirrors must be a list of distinct URLs"),
    ({"decided_by": "cody"}, "decided_by is not names"),
    ({"decided_by": "Cody\nX=1"}, "decided_by is not names"),
    ({"package_index": "https://mirror.example/simple/\nLD_PRELOAD=/tmp/x"}, "package_index is not a URL"),
    ({"package_index": "https://mirror.example/simple/ --extra"}, "package_index is not a URL"),
    ({"llm_url": "file:///etc/passwd"}, "llm_url is not a URL"),
    ({"llm_url": "http://llm.example:99999/v1"}, "llm_url is not a URL"),
    ({"llm_url": "http://llm.example:0/v1"}, "llm_url is not a URL"),
    ({"llm_url": "https://."}, "llm_url is not a URL"),
    ({"release_mirror": "https://mirror..example"}, "release_mirror is not a URL"),
    ({"release_mirror": 7}, "release_mirror is not a URL"),
    ({"bot_email": "bot@example\nX=1"}, "bot_email is not an email address"),
    ({"release_mirror": "https://mirror.example/github.com/"}, "release_mirror must not end in /"),
], ids=lambda value: str(value)[:40])
def test_an_invalid_manifest_fails_and_says_why(tmp_path: Path, change: dict, problem: str) -> None:
    data = {k: v for k, v in {**GOOD, **change}.items() if v is not None}
    for command in ("env", "check"):
        result = run(tmp_path, command, data)
        assert result.returncode != 0
        assert problem in result.stderr
        assert result.stdout == ""


@pytest.mark.parametrize("key", ["llm_url", "package_index", "release_mirror", "bot_email", "decided_by"])
def test_a_bad_value_is_never_echoed_into_the_log(tmp_path: Path, key: str) -> None:
    result = run(tmp_path, "check", {**GOOD, key: SECRET + " x"})
    assert result.returncode != 0
    assert "very-private" not in result.stderr


@pytest.mark.parametrize("text", ["", "{", "[]", '"required"'])
def test_a_file_that_is_not_a_manifest_fails(tmp_path: Path, text: str) -> None:
    result = run(tmp_path, "env", text)
    assert result.returncode != 0
    assert "m0.json" in result.stderr


def test_a_missing_manifest_fails(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, "-I", SCRIPT, "env", str(tmp_path / "none.json")],
                            capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "cannot read the manifest" in result.stderr


@pytest.mark.parametrize("args", [[], ["env"], ["lint", "x"], ["env", "a", "b"], ["visibility", "a"]])
def test_a_bad_command_line_prints_the_usage(args: list[str]) -> None:
    result = subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "Usage:" in result.stderr


def test_check_takes_several_manifests_and_fails_on_any(tmp_path: Path) -> None:
    assert run(tmp_path, "check", GOOD, EXEMPT).stdout.strip() == "2 manifests valid"
    assert run(tmp_path, "check", GOOD, {**GOOD, "ai_review": "no"}).returncode != 0


def test_owners_that_differ_only_in_owner_keys_pass_the_drift_check(tmp_path: Path) -> None:
    public = {**GOOD, "visibility": "public", "mirrors": ["https://backup.example", "https://github.com/acme"],
              "decided_by": "Cody", "bot_email": "issue-archive+other@noreply.example.com"}
    result = run(tmp_path, "drift", GOOD, GOOD, public)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("3 manifests agree on llm_url, ai_review, package_index, release_mirror")


def test_an_exempt_owner_is_drift_on_ai_review_but_not_on_a_missing_model(tmp_path: Path) -> None:
    result = run(tmp_path, "drift", GOOD, EXEMPT)
    assert result.returncode != 0
    assert result.stderr.splitlines() == [f"ai_review differs between {tmp_path}/m0.json | {tmp_path}/m1.json"]


@pytest.mark.parametrize("key", ["llm_url", "package_index", "release_mirror"])
def test_drift_on_a_host_key_fails_and_names_the_files_not_the_values(tmp_path: Path, key: str) -> None:
    result = run(tmp_path, "drift", GOOD, GOOD, {**GOOD, key: SECRET})
    assert result.returncode != 0
    assert result.stderr.strip() == f"{key} differs between {tmp_path}/m0.json, {tmp_path}/m1.json | {tmp_path}/m2.json"


def test_drift_validates_every_manifest_first(tmp_path: Path) -> None:
    result = run(tmp_path, "drift", GOOD, {**GOOD, "bot_email": "nope"})
    assert result.returncode != 0
    assert "bot_email is not an email address" in result.stderr


def repo(name: str, private: bool) -> dict:
    return {"name": name, "full_name": f"acme/{name}", "private": private}


def test_repos_that_follow_the_policy_pass(tmp_path: Path) -> None:
    result = run(tmp_path, "visibility", GOOD, [repo(".project-rules", True), repo("app", True)], [repo("b", True)])
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "3 repos match the owner's policy"


@pytest.mark.parametrize("visibility", ["public", "private"])
def test_a_public_manifest_repo_fails_under_either_policy(tmp_path: Path, visibility: str) -> None:
    result = run(tmp_path, "visibility", {**GOOD, "visibility": visibility}, [repo(".project-rules", False)])
    assert result.returncode != 0
    assert result.stderr.strip() == "acme/.project-rules is public, but the manifest repo is always private"


def test_a_public_repo_under_a_private_owner_is_named(tmp_path: Path) -> None:
    result = run(tmp_path, "visibility", GOOD, [repo("app", True), repo("site", False)])
    assert result.returncode != 0
    assert result.stderr.strip() == "acme/site is public, but the owner's policy is private"


def test_a_private_repo_under_a_public_owner_is_counted_not_named(tmp_path: Path) -> None:
    public = {**GOOD, "visibility": "public"}
    repos = [repo(".project-rules", True), repo("tool", False), repo("secret-plans", True)]
    result = run(tmp_path, "visibility", public, repos)
    assert result.returncode != 0
    assert result.stderr.strip() == "1 private repo(s) under an owner whose policy is public"


def test_a_repo_list_that_cannot_be_read_fails(tmp_path: Path) -> None:
    result = run(tmp_path, "visibility", GOOD, "{")
    assert result.returncode != 0
    assert "cannot read the repo list" in result.stderr


def test_importing_the_script_runs_nothing() -> None:
    spec = importlib.util.spec_from_file_location("manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.validate(GOOD) == []


def test_a_repeated_key_fails_rather_than_the_last_one_winning(tmp_path: Path) -> None:
    text = json.dumps(GOOD)[:-1] + ', "ai_review": {"exempt": "acme/k8s#1"}}'
    result = run(tmp_path, "env", text)
    assert result.returncode != 0
    assert "repeated key 'ai_review'" in result.stderr


def test_the_highest_port_is_a_valid_url(tmp_path: Path) -> None:
    assert run(tmp_path, "check", {**GOOD, "llm_url": "http://llm.example:65535/v1"}).returncode == 0
