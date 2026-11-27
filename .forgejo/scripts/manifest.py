#!/usr/bin/env python3
"""Validate an owner's `.project-rules` manifest (env.json) and hand its values to a job.

Usage:
  manifest.py check FILE...             validate each manifest
  manifest.py env FILE                  validate, then print KEY=value lines for $GITHUB_ENV
  manifest.py drift FILE...             validate each, then fail if their host keys differ
  manifest.py visibility FILE REPOS...  fail on a repo (a JSON list from the repos API) whose
                                        visibility breaks the owner's policy

Every owner keeps its own manifest at `<owner>/.project-rules` on its git host, and the jobs read
the one of the repo they run in (SisyphusMD/project-rules#133). Owner keys say what the owner
decides; host keys repeat the git host's settings in each owner's manifest. There are no
defaults: a missing key, an unknown key or a malformed value fails, so the gate never runs on a
guess. Values go into $GITHUB_ENV and into commands, so each is checked against a strict pattern.
Messages name keys, never values: a public repo's job log is public, and the manifest is not.
"""
import json
import re
import sys

PORT = r"(?:[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])"
LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
HOST = rf"{LABEL}(?:\.{LABEL})*"
URL = re.compile(rf"https?://{HOST}(:{PORT})?(/[A-Za-z0-9._~%/+-]*)?")
EMAIL = re.compile(rf"[A-Za-z0-9._+-]+@{HOST}\.[A-Za-z]{{2,}}")
# Names joined by commas and "and", as rule 2's `Decided by:` line writes them.
NAMES = re.compile(r"[A-Z][A-Za-z'-]*(?:(?:, | and )[A-Z][A-Za-z'-]*)*")
# `.` and `..` are no owner or repo; a dot-leading name such as `.project-rules` is.
ISSUE = re.compile(r"(?!\.{1,2}/)[\w.-]+/(?!\.{1,2}#)[\w.-]+#[1-9][0-9]*")
VISIBILITY = ("public", "private")
# key: (env name or None, pattern, required when AI review is exempt)
KEYS = {
    "visibility": ("VISIBILITY", None, True),
    "mirrors": (None, None, True),
    "decided_by": (None, NAMES, True),
    "bot_email": ("BOT_EMAIL", EMAIL, True),
    "llm_url": ("LLM_URL", URL, False),
    "package_index": ("PACKAGE_INDEX", URL, True),
    "release_mirror": ("RELEASE_MIRROR", URL, True),
}
# The git host's settings: every owner on one host repeats them, and drift compares only these.
HOST_KEYS = ("llm_url", "ai_review", "package_index", "release_mirror")


def problem(key, value, pattern):
    if key == "visibility":
        return None if value in VISIBILITY else 'visibility must be "public" or "private"'
    if key == "mirrors":
        good = isinstance(value, list) and value and all(isinstance(v, str) and URL.fullmatch(v) for v in value)
        return None if good and len(set(value)) == len(value) else "mirrors must be a list of distinct URLs"
    if isinstance(value, str) and pattern.fullmatch(value):
        return None
    kind = {id(EMAIL): "an email address", id(NAMES): "names such as 'Cody and Anna'"}.get(id(pattern), "a URL")
    return f"{key} is not {kind}"


def validate(data):
    """The manifest's problems, one line each; empty when it is valid."""
    if not isinstance(data, dict):
        return ["the manifest is not a JSON object"]
    problems = [f"unknown key {k!r}" for k in sorted(set(data) - set(KEYS) - {"ai_review"})]
    review = data.get("ai_review")
    exempt = isinstance(review, dict)
    if review != "required" and not (exempt and set(review) == {"exempt"}
                                     and isinstance(review["exempt"], str)
                                     and ISSUE.fullmatch(review["exempt"])):
        problems.append('ai_review must be "required" or {"exempt": "owner/repo#n"} citing an open issue')
    for key, (_, pattern, always) in KEYS.items():
        if key not in data:
            if always or not exempt:
                problems.append(f"missing key {key!r}")
        elif found := problem(key, data[key], pattern):
            problems.append(found)
    # Jobs append a path to it, so a trailing slash would double up.
    if isinstance(data.get("release_mirror"), str) and data["release_mirror"].endswith("/"):
        problems.append("release_mirror must not end in /")
    return problems


def unique(pairs):
    # json keeps the last of a repeated key, which would let a second ai_review override the first.
    keys = [k for k, _ in pairs]
    repeated = sorted({k for k in keys if keys.count(k) > 1})
    if repeated:
        raise ValueError(f"repeated key {', '.join(map(repr, repeated))}")
    return dict(pairs)


def read_json(path, what):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f, object_pairs_hook=unique)
    except (OSError, ValueError) as e:
        # json's messages give a position or a key name, never the text around it.
        sys.exit(f"{path}: cannot read the {what}: {e}")


def load(path):
    data = read_json(path, "manifest")
    problems = validate(data)
    if problems:
        sys.exit("\n".join(f"{path}: {p}" for p in problems))
    return data


def env_lines(data):
    review = data["ai_review"]
    lines = [f"AI_REVIEW={'required' if review == 'required' else 'exempt'}",
             f"AI_REVIEW_EXEMPT={'' if review == 'required' else review['exempt']}"]
    lines += [f"{name}={data[key]}" for key, (name, _, _) in KEYS.items() if name and key in data]
    return lines


def drift(manifests):
    """One line per host key whose value differs between the given manifests."""
    lines = []
    for key in HOST_KEYS:
        # An exempt owner may leave llm_url out; the others must still agree.
        values = {path: json.dumps(data[key], sort_keys=True) for path, data in manifests.items() if key in data}
        if len(set(values.values())) > 1:
            groups = {}
            for path, value in values.items():
                groups.setdefault(value, []).append(path)
            lines.append(f"{key} differs between " + " | ".join(", ".join(g) for g in groups.values()))
    return lines


def violations(data, repos):
    """Repos whose visibility breaks the owner's policy; the manifest repo is private either way.
    A public repo is named; a private one only counted, since this runs where its log is public."""
    lines = [f"{r['full_name']} is public, but the manifest repo is always private"
             for r in repos if r["name"] == ".project-rules" and not r["private"]]
    wrong = [r for r in repos if r["name"] != ".project-rules"
             and bool(r["private"]) != (data["visibility"] == "private")]
    lines += [f"{r['full_name']} is public, but the owner's policy is private" for r in wrong if not r["private"]]
    hidden = sum(1 for r in wrong if r["private"])
    if hidden:
        lines.append(f"{hidden} private repo(s) under an owner whose policy is public")
    return lines


def main(argv):
    counts = {"check": (1, None), "env": (1, 1), "drift": (1, None), "visibility": (2, None)}
    if not argv or argv[0] not in counts or len(argv) - 1 < counts[argv[0]][0] or (
            counts[argv[0]][1] and len(argv) - 1 > counts[argv[0]][1]):
        sys.exit(__doc__)
    command, paths = argv[0], argv[1:]
    if command == "visibility":
        data = load(paths[0])
        repos = [r for path in paths[1:] for r in read_json(path, "repo list")]
        found = violations(data, repos)
        if found:
            sys.exit("\n".join(found))
        print(f"{len(repos)} repos match the owner's policy")
        return
    manifests = {path: load(path) for path in paths}
    if command == "env":
        print("\n".join(env_lines(manifests[paths[0]])))
    elif command == "drift":
        found = drift(manifests)
        if found:
            sys.exit("\n".join(found))
        print(f"{len(paths)} manifests agree on {', '.join(HOST_KEYS)}")
    else:
        print(f"{len(paths)} manifests valid")


if __name__ == "__main__":
    main(sys.argv[1:])
