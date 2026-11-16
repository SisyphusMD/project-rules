# #18 ci: accept owner/repo#n issue links

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:27-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#18 (pull request, opened by cody on 2026-11-16, merged 2026-11-16). Branch `refs/pull/18/head` into `main`._

Closes #17
Refs #2

Rule 6 allows `Closes owner/repo#n`, but `Issue link` only matched `#n`, so a k8s or macos PR for Casa work could not name its issue. It now accepts both. Same-repo refs are read with the job token as before. Other repos are read with `ISSUE_READ_TOKEN`, a read:issue-only secret on the org and user (technical call on #2), because a probe showed the job token gets 404 on any other private repo. Writing the own repo out (`bryantserver/project-rules#2`) counts as same-repo, case-insensitively. A cross-repo ref with no secret set fails with that reason instead of a misleading "does not exist".

Tests (`tests/test_issue_link.py`, 9) run against a fake Forgejo where the job token cannot see other repos: which token reads which ref, mixed refs, no ref, a missing cross-repo issue, a PR number, the missing secret, and a 500 that must not pass. Against the old script 7 of them fail.

This PR's own `Issue link` runs main's old copy, which is why it also says `Closes #17`.

## cody, 2026-11-16T14:07:27-08:00

_forgejo-actions, 2026-11-16 11:57:_

**AI review** of `9d19885645`: Clean, well-tested change that extends issue-link validation to accept `owner/repo#n` references with appropriate token routing and clear error messages. The 9 tests cover all meaningful paths (same-repo, cross-repo, case-insensitive own-repo, mixed, missing, PR, no-token, 500). No correctness, security, or test-coverage gaps found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
