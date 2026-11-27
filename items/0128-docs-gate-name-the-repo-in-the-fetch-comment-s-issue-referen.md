# #128 docs(gate): name the repo in the fetch comment's issue reference

- Kind: pull, state: closed, by cody, created 2026-11-24T19:09:01-08:00
- Labels: none; milestone: none
- refs/pull/128/head -> main, merged: True

Refs #78

The fetch step is copied into every repo, where a bare `#78` points at that repo's own issue 78. The comment now says `SisyphusMD/project-rules#78`. Comment only, before the remaining repos copy it.

## forgejo-actions, 2026-11-24T19:09:15-08:00

<!-- ai-review -->
**AI review** of `1d00bdf4b5`: Comment-only change replacing bare `#78` with `SisyphusMD/project-rules#78` in four fetch-step comments across three workflow files, so the issue reference stays unambiguous when the file is copied into other repos. Minimal, correct, and directly serves issue #78.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
