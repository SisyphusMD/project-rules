#!/usr/bin/env python3
"""Fail a PR that changes code without changing tests.

Usage: tests-with-code.py <base-sha> <head-sha>
Env: GITHUB_EVENT_PATH (or PR_BODY).
Code is any source file or tracked executable outside a test path and outside .forgejo/ (CI
tooling, proven by live runs). A test path is a `tests/` or `test/` directory, or a `test_*` / `*_test.*` / `*.test.*`
file. An escape hatch, `No tests: <reason>` in the PR description, lets docs-shaped or
generated-code PRs through; the AI review judges the reason.
"""
import json
import os
import re
import subprocess
import sys

CODE_EXT = {".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".go", ".rs", ".swift", ".kt", ".java",
            ".rb", ".sh", ".zsh", ".c", ".h", ".cc", ".cpp", ".cs", ".php"}


def pr_body():
    # The event payload, not the environment: Linux refuses an environment string over
    # 128 KB, and Renovate bodies with many releases' notes pass that. PR_BODY overrides it.
    if "PR_BODY" in os.environ:
        return os.environ["PR_BODY"]
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        sys.exit("Cannot read the PR description: GITHUB_EVENT_PATH is not set.")
    with open(path, encoding="utf-8") as f:
        event = json.load(f)
    if "pull_request" not in event:
        sys.exit("Cannot read the PR description: this event is not a pull request.")
    return event["pull_request"].get("body") or ""


def is_test(path):
    parts = path.split("/")
    name = parts[-1]
    return (any(p in ("tests", "test", "__tests__") for p in parts[:-1])
            or name.startswith("test_") or re.search(r"(_test|\.test|\.spec)\.[^.]+$", name) is not None)


def is_code(path, modes):
    return (not path.startswith(".forgejo/") and not is_test(path)
            and ("100755" in modes or os.path.splitext(path)[1] in CODE_EXT))


def changes(base, head):
    """Yield (status letter, (old mode, new mode), path) for every change but a deletion."""
    out = subprocess.check_output(
        ["git", "diff", "--raw", "-z", "-M", "--diff-filter=ACMRT", f"{base}...{head}"])
    # -z: ":oldmode newmode oldsha newsha STATUS\0path\0", or for a rename or copy old\0new\0.
    fields = iter(os.fsdecode(out).split("\0"))
    for meta in fields:
        if not meta:
            break
        old, new, _, _, status = meta.lstrip(":").split(" ")
        path = next(fields)
        if status[0] in "RC":
            path = next(fields)
        yield status[0], (old, new), path


def main(base, head):
    found = list(changes(base, head))
    # Either mode: dropping the executable bit in the same change does not make it not code.
    code = [path for _, modes, path in found if is_code(path, modes)]
    # A type change (a symlink becoming a file) is not a test change on its own.
    tests = [path for status, _, path in found if status != "T" and is_test(path)]
    if not code:
        print("No code changed.")
        return
    if tests:
        print(f"{len(code)} code file(s) with {len(tests)} test file(s).")
        return
    m = re.search(r"(?im)^[ \t]*No tests:[ \t]*(\S.*)$", pr_body())
    if m:
        print(f"No tests, by the description: {m.group(1).strip()}")
        return
    sys.exit("Code changed without tests:\n  " + "\n  ".join(code)
             + "\nAdd tests, or say `No tests: <reason>` in the PR description.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
