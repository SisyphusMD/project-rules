# #131 docs(gate): name project-rules#78 in full in the caller headers

- Kind: pull, state: closed, by cody, created 2026-11-25T21:37:27-08:00
- Labels: none; milestone: none
- refs/pull/131/head -> main, merged: True

Refs #78

Repos copy `ci.yml` and `ai-review.yml`, and their headers said `(#78)`, which in a copy points at that repo's own issue #78. They now say `SisyphusMD/project-rules#78`. Comment-only; the caller PRs in the other repos already carry the same text.

This is also the first PR here judged by the callers themselves.

No tests: header comments only.

## forgejo-actions, 2026-11-25T21:38:01-08:00

<!-- ai-review -->
**AI review** of `190076e107`: Comment-only change replacing bare `#78` with `SisyphusMD/project-rules#78` in the two caller workflow headers so copies in other repos point at the right issue. CHANGELOG entry added. Clean, minimal, and correct.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
