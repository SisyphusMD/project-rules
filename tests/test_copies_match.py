"""The Copies match gate check (#141): what counts as a copy falling behind, and what may differ."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".forgejo/scripts/copies-match.py"
SPEC = importlib.util.spec_from_file_location("copies_match", SCRIPT)
match = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(match)

CI = (ROOT / ".forgejo/workflows/ci.yml").read_text()
REVIEW = (ROOT / ".forgejo/workflows/ai-review.yml").read_text()
ARCHIVE = (ROOT / ".forgejo/workflows/issue-archive.yml").read_text()
LINT_CALL = "  shared-lint:\n    uses: SisyphusMD/project-rules/.forgejo/workflows/gate-lint.yml@main\n"
OWN_LINT = """
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - run: true
  secrets:
    name: Secrets
    runs-on: ubuntu-latest
    steps:
      - run: true
"""


def drop_lint(text: str) -> str:
    start = text.index(LINT_CALL)
    rest = text[start + len(LINT_CALL):]
    # The call's secrets mapping goes with it.
    while rest.startswith("    "):
        rest = rest.split("\n", 1)[1] if "\n" in rest else ""
    return text[:start] + rest


def drop_issue_token(text: str) -> str:
    lines = [line for line in text.splitlines(keepends=True)
             if "ISSUE_READ_TOKEN" not in line and "read:issue only" not in line]
    # A mapping left empty goes too.
    return "".join(line for i, line in enumerate(lines)
                   if not (line == "    secrets:\n"
                           and not (i + 1 < len(lines) and lines[i + 1].startswith("      "))))


def test_the_canonical_callers_have_what_the_rules_below_rely_on() -> None:
    assert LINT_CALL in CI
    assert match.ISSUE_TOKEN in CI.splitlines() and match.ISSUE_TOKEN in REVIEW.splitlines()
    assert "branches: [main]" in CI


# --- callers -----------------------------------------------------------------------------------

@pytest.mark.parametrize("text", [CI, REVIEW, ARCHIVE])
def test_an_identical_caller_passes(text: str) -> None:
    assert match.compare_caller(text, text) == []


def test_comments_and_blank_lines_do_not_count() -> None:
    edited = "# reworded header\n\n" + CI.replace("concurrency:", "# a note\nconcurrency:")
    assert match.compare_caller(CI, edited) == []


def test_the_issue_token_mapping_may_be_dropped() -> None:
    assert match.compare_caller(CI, drop_issue_token(CI)) == []
    assert match.compare_caller(REVIEW, drop_issue_token(REVIEW)) == []


def test_the_manifest_token_may_not_be_dropped() -> None:
    gone = "".join(line for line in REVIEW.splitlines(keepends=True) if "PROJECT_RULES_TOKEN" not in line)
    assert match.compare_caller(REVIEW, gone) == ["job shared-review differs"]


def test_another_secret_in_its_place_is_drift() -> None:
    other = CI.replace("${{ secrets.ISSUE_READ_TOKEN }}", "${{ secrets.ADMIN_TOKEN }}")
    assert match.compare_caller(CI, other) == ["job shared-gate differs"]


def test_own_lint_and_secrets_may_replace_shared_lint() -> None:
    assert match.compare_caller(CI, drop_lint(CI) + OWN_LINT) == []


def test_dropping_shared_lint_without_a_replacement_is_drift() -> None:
    assert match.compare_caller(CI, drop_lint(CI)) == ["job shared-lint is missing"]


def test_own_lint_beside_shared_lint_is_drift() -> None:
    assert match.compare_caller(CI, CI + OWN_LINT) == ["own Lint or Secrets beside shared-lint"]


def test_other_jobs_of_its_own_are_allowed() -> None:
    assert match.compare_caller(CI, CI + "  deploy:\n    runs-on: ubuntu-latest\n") == []


def test_one_preview_branch_may_join_main_in_ci_only() -> None:
    preview = CI.replace("branches: [main]", "branches: [main, staging]")
    assert match.compare_caller(CI, preview, preview=True) == []
    assert match.compare_caller(CI, preview) == ["name, triggers or concurrency differ"]
    for other in ("[staging, main]", "[main, a, b]", "[dev]"):
        assert match.compare_caller(CI, CI.replace("[main]", other, 1), preview=True) == [
            "name, triggers or concurrency differ"], other


def test_project_rules_matches_itself_although_it_holds_the_retired_files() -> None:
    assert (ROOT / match.RETIRED[0]).exists()
    assert match.check(ROOT, ROOT, private=False) == []


def test_a_changed_schedule_or_pin_is_drift() -> None:
    assert match.compare_caller(ARCHIVE, ARCHIVE.replace("17 10", "0 0")) == [
        "name, triggers or concurrency differ"]
    assert match.compare_caller(CI, CI.replace("gate.yml@main", "gate.yml@v1")) == [
        "job shared-gate differs"]


def test_a_missing_shared_call_is_drift() -> None:
    head = REVIEW.split("jobs:")[0]
    assert match.compare_caller(REVIEW, head + "jobs:\n") == ["job shared-review is missing"]
    assert match.compare_caller(REVIEW, head) == [
        "name, triggers or concurrency differ", "job shared-review is missing"]


def test_an_old_full_copy_of_the_archive_job_is_drift() -> None:
    old = ARCHIVE.split("jobs:")[0] + "jobs:\n  archive:\n    runs-on: ubuntu-latest\n"
    assert match.compare_caller(ARCHIVE, old) == ["job shared-archive is missing"]


# --- templates ---------------------------------------------------------------------------------

TEMPLATE = "---\nname: Bug\nabout: Wrong\nlabels: [type:bug]\n---\n## What\n"


@pytest.mark.parametrize("path", sorted((ROOT / ".forgejo/issue_template").iterdir()))
def test_every_canonical_template_has_the_keys_compared(path: Path) -> None:
    keys = match.front_matter(path.read_text())
    assert keys is not None and set(keys) == set(match.TEMPLATE_KEYS), path.name


def test_reworded_prompts_pass() -> None:
    reworded = TEMPLATE.replace("about: Wrong", "about: It broke").replace("## What", "## When")
    assert match.compare_template(TEMPLATE, reworded) == []


def test_changed_labels_or_name_is_drift() -> None:
    assert match.compare_template(TEMPLATE, TEMPLATE.replace("[type:bug]", "[bug]")) == [
        "front matter labels differs"]
    assert match.compare_template(TEMPLATE, TEMPLATE.replace("name: Bug", "name: Defect")) == [
        "front matter name differs"]


@pytest.mark.parametrize("text", ["## What\n", "---\nname: Bug\n", ""])
def test_a_template_without_front_matter_is_drift(text: str) -> None:
    assert match.compare_template(TEMPLATE, text) == ["no front matter"]


# --- a whole repo, and the command line --------------------------------------------------------

def faithful(tmp_path: Path, private: bool) -> Path:
    repo = tmp_path / "repo"
    paths = [*match.CALLERS, *(f"{match.TEMPLATES}/{p.name}" for p in (ROOT / match.TEMPLATES).iterdir())]
    if not private:
        paths.append(match.MIRROR_LOCKDOWN)
    for path in paths:
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, repo / path)
    return repo


@pytest.mark.parametrize("private", [True, False])
def test_a_faithful_repo_matches(tmp_path: Path, private: bool) -> None:
    assert match.check(ROOT, faithful(tmp_path, private), private) == []


def test_a_public_repo_needs_mirror_lockdown_and_a_private_one_does_not(tmp_path: Path) -> None:
    repo = faithful(tmp_path, private=True)
    assert match.check(ROOT, repo, private=False) == [f"{match.MIRROR_LOCKDOWN}: missing"]
    (repo / match.MIRROR_LOCKDOWN).parent.mkdir(parents=True)
    (repo / match.MIRROR_LOCKDOWN).write_text("on: push\n")
    assert match.check(ROOT, repo, private=False) == [f"{match.MIRROR_LOCKDOWN}: differs"]


def test_each_kind_of_difference_is_reported(tmp_path: Path) -> None:
    repo = faithful(tmp_path, private=True)
    (repo / match.CALLERS[1]).unlink()
    (repo / match.CALLERS[0]).write_text(drop_lint(CI))
    (repo / f"{match.TEMPLATES}/bug.md").unlink()
    (repo / f"{match.TEMPLATES}/spike.md").write_text("no front matter")
    (repo / match.RETIRED[0]).parent.mkdir(parents=True)
    (repo / match.RETIRED[0]).write_text("old copy")
    assert match.check(ROOT, repo, True) == [
        ".forgejo/workflows/ci.yml: job shared-lint is missing",
        ".forgejo/workflows/ai-review.yml: missing",
        ".forgejo/issue_template/bug.md: missing",
        ".forgejo/issue_template/spike.md: no front matter",
        ".forgejo/scripts/issue-archive.py: runs from project-rules main now; delete this copy",
    ]


def run(repo: Path, private: str | None, monkeypatch, capsys) -> tuple[int, str, str]:
    if private is None:
        monkeypatch.delenv("PRIVATE", raising=False)
    else:
        monkeypatch.setenv("PRIVATE", private)
    code = match.main(["copies-match.py", str(ROOT), str(repo)])
    out = capsys.readouterr()
    return code, out.out, out.err


def test_the_command_passes_a_faithful_repo(tmp_path: Path, monkeypatch, capsys) -> None:
    assert run(faithful(tmp_path, private=True), "true", monkeypatch, capsys)[:2] == (
        0, "every copied file matches project-rules main\n")


def test_the_command_fails_and_lists_each_difference(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = faithful(tmp_path, private=False)
    (repo / match.CALLERS[2]).unlink()
    code, out, err = run(repo, "false", monkeypatch, capsys)
    assert (code, out) == (1, ".forgejo/workflows/issue-archive.yml: missing\n")
    assert "Copy each file again" in err


@pytest.mark.parametrize("private", [None, "yes"])
def test_the_command_refuses_without_a_clear_visibility(tmp_path: Path, private: str | None,
                                                        monkeypatch, capsys) -> None:
    code, _, err = run(faithful(tmp_path, private=True), private, monkeypatch, capsys)
    assert code == 2 and f"got {private!r}" in err


def test_the_script_runs_as_a_command(tmp_path: Path) -> None:
    done = subprocess.run([sys.executable, "-I", str(SCRIPT), str(ROOT), str(faithful(tmp_path, True))],
                          env={"PRIVATE": "true"}, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stderr


def test_the_command_refuses_the_wrong_arguments(monkeypatch, capsys) -> None:
    monkeypatch.setenv("PRIVATE", "true")
    assert match.main(["x"]) == 2
    assert "Usage" in capsys.readouterr().err


def test_a_workflow_without_jobs_has_no_jobs() -> None:
    assert match.jobs(["name: x"]) == (["name: x"], {})
