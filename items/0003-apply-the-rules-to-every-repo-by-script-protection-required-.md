# #3 Apply the rules to every repo by script: protection, required checks and backup mirror

- Kind: issue, state: open, by cody, created 2026-11-16T14:07:21-08:00
- Labels: status:ready, type:feature; milestone: none

_Recreated from bryantserver/project-rules#3 (issue, opened by cody on 2026-11-16)._

Depends on #2. No list of following repos (decision on #1): a script walks every repo on the primary Forgejo and applies or reports branch protection, required checks and a private repo push mirror, with per-repo exceptions (bots, break-glass) declared here. Repos not yet brought in are tracked as issues (#4-#7) and reported, not silently skipped.
