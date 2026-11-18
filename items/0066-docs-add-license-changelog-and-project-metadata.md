# #66 docs: add LICENSE, CHANGELOG and project metadata

- Kind: pull, state: closed, by cody, created 2026-11-17T07:20:11-08:00
- Labels: none; milestone: none
- refs/pull/66/head -> main, merged: True

Closes #59.

- `LICENSE`: MIT, with the reasoning in `CONTRIBUTING.md` (files here are vendored into MIT and GPL-3.0 consumers, and only a permissive licence sits under both).
- `CHANGELOG.md` in Keep a Changelog form, with the 0.2.0 and 0.3.0 releases and an Unreleased section.
- `pyproject.toml`: a metadata-only `[project]` table with the SPDX licence and project URLs, and a Hatchling backend named so no tool falls back to setuptools.
- `CONTRIBUTING.md`: a Releases section (a release is a tag on main; move Unreleased and set the version first).
- `tests/test_release_metadata.py`: pyproject and the newest changelog release must agree, there is one Unreleased section, and on a tag run (`RELEASE_TAG`, set in `tests.yml`) the tag must match. The tag check fails for a mismatched tag and passes for v0.3.0.

The template and adoption guide still do not ask other repos for these; that is #65.

## forgejo-actions, 2026-11-17T07:21:20-08:00

<!-- ai-review -->
**AI review** of `0ced3cd25c`: Clean, well-scoped PR that adds LICENSE, CHANGELOG, pyproject metadata, and a consistency test as required by issue #59. All hunks map to the issue, tests cover the new metadata-agreement behaviour, and the workflow change is the minimum needed to enable the tag check.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
