# #14 Diff size check

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:24-08:00
- Labels: type:feature; milestone: none

_Recreated from bryantserver/project-rules#14 (issue, opened by cody on 2026-11-16, closed 2026-11-16)._

Part of #2. Rule 8's 400-line limit as a CI job: lines changed outside tests and lockfiles, from base...head; over 400 fails unless the description says `Large diff: <reason>`. Script runs from main's copy like Tests with code. Ships with tests. After merge, add `CI / Diff size (pull_request_target)` to main's required checks once a real PR has shown a pass and a deliberate fail.

## cody, 2026-11-16T14:07:25-08:00

_cody, 2026-11-16 08:18:_

Merged in #15 (6c372ed). Not required yet: next, one real PR must show Diff size passing and a throwaway PR over 400 lines must show it failing, then `CI / Diff size (pull_request_target)` joins main's required checks.

## cody, 2026-11-16T14:07:25-08:00

_cody, 2026-11-16 11:57:_

Proven: throwaway PR #16 (401 lines, no reason) failed Diff size ('401 changed lines ... over the 400 limit'), then closed and its branch deleted; PR #18 passed it. `CI / Diff size (pull_request_target)` is now a required check on main.
