import json
import subprocess
import sys
from pathlib import Path

import pytest

VERIFY = Path(__file__).resolve().parents[1] / "shared/packaging/verify-release-pr.py"
REPO = "Owner/Project"
CHANGELOG = "## [Unreleased]\n\n## [1.2.3] - 2026-11-17\n"


@pytest.fixture
def release(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()

    git("init", "-b", "main")
    git("config", "user.name", "Release test")
    git("config", "user.email", "release@example.test")
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [Unreleased]\n")
    git("add", "--", "CHANGELOG.md")
    git("commit", "-m", "base")
    git("tag", "-a", "-m", "previous release", "v1.2.2")
    remote = tmp_path.with_suffix(".git")
    git("init", "--bare", str(remote))
    git("remote", "add", "origin", str(remote))
    git("push", "origin", "main", "v1.2.2")
    git("switch", "-c", "release/v1.2.3")
    changelog.write_text(CHANGELOG)
    git("commit", "-am", "prepare 1.2.3")
    head = git("rev-parse", "HEAD")
    git("switch", "main")
    git("merge", "--no-ff", "-m", "merge release", head)
    merge = git("rev-parse", "HEAD")
    git("commit", "--allow-empty", "-m", "unrelated change after merge")
    pr = {
        "number": 7, "state": "closed", "merged": True, "merge_commit_sha": merge,
        "base": {"ref": "main", "repo": {"full_name": REPO}},
        "head": {
            "label": "release/v1.2.3", "ref": "release/v1.2.3", "sha": head,
            "repo": {"full_name": REPO},
        },
    }

    def run(number="7"):
        return subprocess.run(
            [sys.executable, VERIFY, REPO, number, git("rev-parse", "main")],
            input=json.dumps(pr), text=True, cwd=tmp_path, capture_output=True, check=False,
        )

    return pr, git, run


def test_authorizes_the_merge_commit_after_main_moves(release):
    pr, _, run = release
    result = run()
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"tag=v1.2.3\ncommit={pr['merge_commit_sha']}\n"


def test_authorizes_after_the_release_branch_is_deleted(release):
    pr, git, run = release
    git("branch", "-d", "release/v1.2.3")
    pr["head"]["ref"] = "refs/pull/7/head"
    result = run()
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("side", "key", "value", "message"),
    [
        (None, "merged", False, "has not merged"),
        (None, "number", 8, "has not merged"),
        (None, "merge_commit_sha", None, "full commit SHAs"),
        ("base", "ref", "stable", "into main"),
        ("head", "repo", {"full_name": "Fork/Project"}, "in this repository"),
        ("head", "ref", "other/v1.2.3", "head branch"),
        ("head", "ref", "release/v01.2.3", "head branch"),
        ("head", "ref", "refs/pull/8/head", "head branch"),
    ],
)
def test_refuses_invalid_pull_requests(release, side, key, value, message):
    pr, _, run = release
    (pr if side is None else pr[side])[key] = value
    result = run()
    assert result.returncode != 0
    assert message in result.stderr
    assert not result.stdout


def test_refuses_a_tag_that_does_not_match_the_changelog(release):
    pr, _, run = release
    pr["head"].update(label="release/v1.2.4", ref="release/v1.2.4")
    assert "CHANGELOG.md" in run().stderr


def test_refuses_a_second_parent(release):
    pr, _, run = release
    pr["merge_commit_sha"] = pr["head"]["sha"]
    assert "not on" in run().stderr


def test_refuses_a_different_tree(release):
    pr, git, run = release
    pr["head"]["sha"] = git("rev-parse", f"{pr['merge_commit_sha']}^1")
    assert "differs" in run().stderr


def test_existing_tag_must_match_the_annotated_release(release):
    pr, git, run = release
    git("tag", "v1.2.3", pr["merge_commit_sha"])
    git("push", "origin", "v1.2.3")
    assert "existing tag" in run().stderr
    git("push", "origin", ":refs/tags/v1.2.3")
    git("tag", "-d", "v1.2.3")
    git("tag", "-a", "-m", "release", "v1.2.3", pr["merge_commit_sha"])
    git("push", "origin", "v1.2.3")
    assert run().returncode == 0


def test_refuses_late_release_that_would_go_backwards(release):
    _, git, run = release
    git("tag", "-a", "-m", "newer release", "v1.2.4")
    git("push", "origin", "v1.2.4")
    git("tag", "-d", "v1.2.4")
    assert "newer" in run().stderr


def test_push_protects_main_and_existing_tags(release, tmp_path, monkeypatch):
    pr, git, _ = release
    git("push", "origin", "main")
    original_main = git("rev-parse", "main")
    git("commit", "--allow-empty", "-m", "clone-only change")
    target = pr["merge_commit_sha"]

    fake_bin = tmp_path / ".git" / "test-bin"
    fake_bin.mkdir()
    for name in ("curl", "sleep"):
        command = fake_bin / name
        command.write_text("#!/bin/sh\nexit 1\n" if name == "curl" else "#!/bin/sh\nexit 0\n")
        command.chmod(0o700)
    monkeypatch.setenv("PATH", f"{fake_bin}:/usr/bin:/bin")
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://forge.example.test")

    def push(commit):
        return subprocess.run(
            ["bash", VERIFY.with_name("push-tag.sh"), "v1.2.3", "stub", "--merged-commit", commit],
            cwd=tmp_path, capture_output=True, text=True, check=False,
        )

    git("tag", "-a", "-m", "first attempt", "v1.2.3", target)
    initial = push(target)
    assert initial.returncode == 0, initial.stderr
    advertised = git("ls-remote", "origin", "refs/tags/v1.2.3", "refs/tags/v1.2.3^{}")
    assert f"{target}\trefs/tags/v1.2.3^{{}}" in advertised
    assert git("ls-remote", "origin", "refs/heads/main") == f"{original_main}\trefs/heads/main"

    git("tag", "-f", "-a", "-m", "second attempt", "v1.2.3", target)
    retry = push(target)
    assert retry.returncode == 0, retry.stderr
    git("tag", "-f", "-a", "-m", "other commit", "v1.2.3", original_main)
    conflicting = push(original_main)
    assert conflicting.returncode != 0
    assert git("ls-remote", "origin", "refs/tags/v1.2.3", "refs/tags/v1.2.3^{}") == advertised
