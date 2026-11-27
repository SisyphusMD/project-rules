# #127 feat(ai-review): read RULES.md from project-rules main with the script

- Kind: pull, state: closed, by cody, created 2026-11-24T19:03:50-08:00
- Labels: none; milestone: none
- refs/pull/127/head -> main, merged: True

Refs #78

Each repo carried `.forgejo/RULES.md` for the AI review, and nine of 14 copies were out of date, so reviews there judged by old rules. The reviewer now reads `RULES.md` from the same project-rules checkout it runs from, and a missing file fails the check instead of reviewing without rules. Decided on #78 (2026-11-24), which changes rule 22: no repo keeps a copy.

`CONTRIBUTING.md` and `README.md` still come from the reviewed repo's main. A repo deletes its copy in the PR that moves it to the fetched scripts, since an older reviewer copy still reads it.

`tests/test_ai_review_context.py` rejects rules taken from the checkout, and runs the whole review from a script whose tree has no `RULES.md`: the old reviewer asked the model anyway, using the repo's stale copy.


## forgejo-actions, 2026-11-24T19:04:26-08:00

<!-- ai-review -->
**AI review** of `a2d1280736`: Clean, well-scoped change that moves RULES.md reading from the reviewed repo's checkout to the project-rules script tree, with proper fail-closed behavior and adequate tests. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
