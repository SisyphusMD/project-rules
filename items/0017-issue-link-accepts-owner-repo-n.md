# #17 Issue link accepts owner/repo#n

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:26-08:00
- Labels: type:feature; milestone: none

_Recreated from bryantserver/project-rules#17 (issue, opened by cody on 2026-11-16, closed 2026-11-16)._

Part of #2. RULES.md rule 6 allows `Closes owner/repo#n`, but issue-link.py accepts only same-repo #n, so a private repo or a private repo PR for a private repo work fails. Check cross-repo refs with ISSUE_READ_TOKEN (technical call on #2); same-repo refs keep using the job token.

## cody, 2026-11-16T14:07:26-08:00

_cody, 2026-11-16 11:57:_

Merged in #18 (f317a7a). Cross-repo refs are checked with ISSUE_READ_TOKEN.
