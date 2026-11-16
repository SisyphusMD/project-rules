# #20 ci: AI review reads the rules, CONTRIBUTING.md and the linked issues

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:28-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#20 (pull request, opened by cody on 2026-11-16, merged 2026-11-16). Branch `refs/pull/20/head` into `main`._

Closes #19
Refs #2

The reviewer read only README.md, which no longer holds the rules here (and won't anywhere once repos adopt them), and it never saw the issue a PR is for, so it could not judge rule 7 (every hunk maps to the issue). Now its prompt carries, all from main: the project rules (`.forgejo/RULES.md`, the synced copy other repos will carry, or `RULES.md` here), `CONTRIBUTING.md`, and README.md for what the project is. It also gets each issue the PR names, same-repo or `owner/repo#n` (read with `ISSUE_READ_TOKEN`), with its body and latest ten comments. Comments are paged so "latest" is right on long issues, and the body and each comment are capped separately so a long body never pushes out the newest decision. A missing or hidden issue is noted for the reviewer; any other error fails the review closed. Scope creep and an unsound `No tests:` or `Large diff:` reason are now blocking (technical call on #19). `docs/new-project.md` says to copy `RULES.md` to `.forgejo/RULES.md`.

Tests (`tests/test_ai_review_context.py`, 10): which rules file wins, missing files, the issue token per repo, the last ten comments across two pages, a 50,000-character body keeping the latest comment, a missing issue, a 503 that must raise, no refs. The context tests error against the old script (no `linked_issues`).

This PR is reviewed by main's old reviewer; the next PR is the first reviewed with the new context.

## cody, 2026-11-16T14:07:28-08:00

_forgejo-actions, 2026-11-16 12:02:_

**AI review** of `b5c70bbe61`: Clean, well-tested PR that extends the AI reviewer's context with project rules, CONTRIBUTING.md, and linked issues. The regex, pagination, error handling, and fail-closed policy are all correct, and the 10 tests cover the important paths.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
