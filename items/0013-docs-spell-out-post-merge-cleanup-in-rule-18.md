# #13 docs: spell out post-merge cleanup in rule 18

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:24-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#13 (pull request, opened by cody on 2026-11-16, merged 2026-11-16). Branch `refs/pull/13/head` into `main`._

Closes #12

Rule 18 said only "then delete the branch", so leftovers depended on whoever merged remembering them. It now lists the cleanup that follows every verified merge: the branch on the server and locally, prune, fast-forward local `main` checkouts, worktrees and scratch, dependents moved to `status:ready`, and the status comment. It keeps the guard that a branch `main` does not contain is never deleted.

No tests: rule text only.

## cody, 2026-11-16T14:07:24-08:00

_forgejo-actions, 2026-11-16 08:02:_

**AI review** of `c4394bc2f0`: Documentation-only change expanding rule 18 with explicit post-merge cleanup steps and a safety guard against deleting branches not yet in main. No code changes, no tests needed, no issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
