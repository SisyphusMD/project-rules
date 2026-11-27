#!/usr/bin/env python3
"""Fail when this repo's copies of project-rules files differ from main.

Usage: copies-match.py CANONICAL REPO   (env PRIVATE: "true" for a private repo)

CANONICAL is project-rules main as the gate fetched it; REPO is the PR head. docs/adopting.md
has every repo copy a few files, and only this check notices when a copy falls behind (#141). Each
repo checks only its own files in its own run, so it needs no token and prints nothing of another
repo. The callers follow the rule in docs/adopting.md rather than bytes; mirror-lockdown.yml (public
repos only) matches byte for byte; an issue template may reword its prompts but keeps `name` and
`labels`. Comments do not count, and nothing else in a caller's header may differ: its name,
triggers, schedule and concurrency are the canonical ones.
"""
import os
import re
import sys
from pathlib import Path

CALLERS = (".forgejo/workflows/ci.yml", ".forgejo/workflows/ai-review.yml",
           ".forgejo/workflows/issue-archive.yml")
MIRROR_LOCKDOWN = ".github/workflows/mirror-lockdown.yml"
TEMPLATES = ".forgejo/issue_template"
# Copied once and now run from main: a copy left behind reads as live code but runs nowhere.
RETIRED = (".forgejo/scripts/issue-archive.py",)
TEMPLATE_KEYS = ("name", "labels")
ISSUE_TOKEN = "      ISSUE_READ_TOKEN: ${{ secrets.ISSUE_READ_TOKEN }}"


def strip(text):
    """Lines that carry meaning: no blanks and no comment-only lines."""
    return [line.rstrip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def jobs(lines):
    """(lines up to `jobs:`, {job id: its lines}) of a workflow whose jobs sit at indent 2."""
    if "jobs:" not in lines:
        return lines, {}
    cut = lines.index("jobs:")
    found, current = {}, None
    for line in lines[cut + 1:]:
        match = re.fullmatch(r"  ([\w-]+):", line)
        if match:
            current = match.group(1)
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return lines[:cut + 1], found


def without_issue_token(block):
    """A shared call without its ISSUE_READ_TOKEN mapping, which a repo may drop (adopting.md)."""
    out = [line for line in block if line != ISSUE_TOKEN]
    if out and out[-1] == "    secrets:":
        out.pop()
    return out


def preview_branch(line):
    """`branches: [main, staging]` reads as `[main]`: a repo adds its preview branch (rule 6)."""
    match = re.fullmatch(r"(\s+branches: )\[([^\]]*)\]", line)
    if not match:
        return line
    branches = [b.strip() for b in match.group(2).split(",")]
    return f"{match.group(1)}[main]" if branches[0] == "main" and len(branches) == 2 else line


def names(block):
    return {line.split(":", 1)[1].strip() for line in block if line.startswith("    name:")}


def compare_caller(canonical, theirs, preview=False):
    """How a repo's caller departs from the rule in docs/adopting.md (preview: ci.yml's branches)."""
    head, want = jobs(strip(canonical))
    their_head, have = jobs(strip(theirs))
    if preview:
        their_head = [preview_branch(line) for line in their_head]
    problems = []
    if their_head != head:
        problems.append("name, triggers or concurrency differ")
    own = [job for job in have if job not in want]
    own_names = set().union(*(names(have[job]) for job in own))
    # Its own Lint and Secrets may replace shared-lint, so no check name is posted twice.
    replaces_lint = {"Lint", "Secrets"} <= own_names
    for job, block in want.items():
        if job not in have:
            if not (job == "shared-lint" and replaces_lint):
                problems.append(f"job {job} is missing")
        elif have[job] not in (block, without_issue_token(block)):
            problems.append(f"job {job} differs")
    # Other jobs of its own are allowed; a second Lint or Secrets would post one check twice.
    if "shared-lint" in have and own_names & {"Lint", "Secrets"}:
        problems.append("own Lint or Secrets beside shared-lint")
    return problems


def front_matter(text):
    lines = [line.strip() for line in text.splitlines()]
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return None
    keys = {}
    for line in lines[1:lines.index("---", 1)]:
        key, sep, value = line.partition(":")
        if sep and key.strip() in TEMPLATE_KEYS:
            keys[key.strip()] = value.strip()
    return keys


def compare_template(canonical, theirs):
    want, have = front_matter(canonical), front_matter(theirs)
    if have is None:
        return ["no front matter"]
    return [f"front matter {key} differs" for key in TEMPLATE_KEYS if want.get(key) != have.get(key)]


def check(canonical, repo, private):
    """Each difference as `path: what`, in a fixed order; empty when every copy matches."""
    found = []
    for path in CALLERS:
        if not (repo / path).is_file():
            found.append(f"{path}: missing")
        else:
            found += [f"{path}: {p}" for p in
                      compare_caller((canonical / path).read_text(), (repo / path).read_text(),
                                     preview=path == CALLERS[0])]
    if not private:
        if not (repo / MIRROR_LOCKDOWN).is_file():
            found.append(f"{MIRROR_LOCKDOWN}: missing")
        elif (repo / MIRROR_LOCKDOWN).read_bytes() != (canonical / MIRROR_LOCKDOWN).read_bytes():
            found.append(f"{MIRROR_LOCKDOWN}: differs")
    for template in sorted((canonical / TEMPLATES).iterdir()):
        path = f"{TEMPLATES}/{template.name}"
        if not (repo / path).is_file():
            found.append(f"{path}: missing")
        else:
            found += [f"{path}: {p}" for p in
                      compare_template(template.read_text(), (repo / path).read_text())]
    # project-rules checks itself against itself, and there the retired files are the live ones.
    if canonical.resolve() != repo.resolve():
        found += [f"{path}: runs from project-rules main now; delete this copy"
                  for path in RETIRED if (repo / path).exists()]
    return found


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    if os.environ.get("PRIVATE") not in ("true", "false"):
        print(f"PRIVATE must be true or false (the event's repository.private), got "
              f"{os.environ.get('PRIVATE')!r}", file=sys.stderr)
        return 2
    found = check(Path(argv[1]), Path(argv[2]), os.environ["PRIVATE"] == "true")
    for line in found:
        print(line)
    if found:
        print("Copy each file again from project-rules main (docs/adopting.md says which and what "
              "may differ).", file=sys.stderr)
        return 1
    print("every copied file matches project-rules main")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
