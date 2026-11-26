#!/usr/bin/env python3
"""Validate an owner's `.project-rules` manifest (env.json) and hand its values to a job.

Usage:
  manifest.py check FILE...  validate each manifest
  manifest.py env FILE       validate, then print KEY=value lines for $GITHUB_ENV
  manifest.py drift FILE...  validate each, then fail if the keys meant to match differ

Every owner keeps its own manifest at `<owner>/.project-rules` on its git host, and the jobs read
the one of the repo they run in (SisyphusMD/project-rules#133). There are no defaults: a missing
key, an unknown key or a malformed value fails, so the gate never runs on a guess. Values go into
$GITHUB_ENV and into commands, so each must be a single token with no whitespace or quotes.
"""
import json
import re
import sys

PORT = r"(?:[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])"
LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
HOST = rf"{LABEL}(?:\.{LABEL})*"
URL = re.compile(rf"https?://{HOST}(:{PORT})?(/[A-Za-z0-9._~%/+-]*)?")
EMAIL = re.compile(rf"[A-Za-z0-9._+-]+@{HOST}\.[A-Za-z]{{2,}}")
# A name starts with a word character or dash, so `.` and `..` are no repo.
ISSUE = re.compile(r"[\w-][\w.-]*/[\w-][\w.-]*#[1-9][0-9]*")
# key: (env name, pattern, required when AI review is exempt)
KEYS = {
    "mirror_url": ("MIRROR_URL", URL, True),
    "llm_url": ("LLM_URL", URL, False),
    "package_index": ("PACKAGE_INDEX", URL, True),
    "release_mirror": ("RELEASE_MIRROR", URL, True),
    "bot_email": ("BOT_EMAIL", EMAIL, True),
}
# Settings of the git host, the same for every owner on it; ai_review is each owner's own policy.
SHARED = ("mirror_url", "llm_url", "package_index", "release_mirror", "bot_email")


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
        elif not isinstance(data[key], str) or not pattern.fullmatch(data[key]):
            problems.append(f"{key} is not a valid {'email' if pattern is EMAIL else 'URL'}: {data[key]!r}")
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


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=unique)
    except (OSError, ValueError) as e:
        sys.exit(f"{path}: cannot read the manifest: {e}")
    problems = validate(data)
    if problems:
        sys.exit("\n".join(f"{path}: {p}" for p in problems))
    return data


def env_lines(data):
    review = data["ai_review"]
    lines = [f"AI_REVIEW={'required' if review == 'required' else 'exempt'}",
             f"AI_REVIEW_EXEMPT={'' if review == 'required' else review['exempt']}"]
    lines += [f"{name}={data[key]}" for key, (name, _, _) in KEYS.items() if key in data]
    return lines


def drift(manifests):
    """One line per shared key whose value differs between the given manifests."""
    lines = []
    for key in SHARED:
        # An exempt owner may leave llm_url out; the others must still agree.
        values = {path: data[key] for path, data in manifests.items() if key in data}
        if len(set(values.values())) > 1:
            lines.append(f"{key} differs: " + ", ".join(f"{p}={v!r}" for p, v in values.items()))
    return lines


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "env", "drift") or (argv[0] == "env" and len(argv) != 2):
        sys.exit(__doc__)
    command, paths = argv[0], argv[1:]
    manifests = {path: load(path) for path in paths}
    if command == "env":
        print("\n".join(env_lines(manifests[paths[0]])))
    elif command == "drift":
        found = drift(manifests)
        if found:
            sys.exit("\n".join(found))
        print(f"{len(paths)} manifests agree on {', '.join(SHARED)}")
    else:
        print(f"{len(paths)} manifests valid")


if __name__ == "__main__":
    main(sys.argv[1:])
