# #16 test: Diff size must fail (throwaway, do not merge)

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:26-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#16 (pull request, opened by cody on 2026-11-16, closed 2026-11-16). Branch `refs/pull/16/head` into `main`._

Refs #14

Throwaway: 401 counted lines, no `Large diff:` reason. Expect `CI / Diff size` to fail; then closed and the branch deleted.

No tests: throwaway check of the gate.

## cody, 2026-11-16T14:07:26-08:00

_forgejo-actions, 2026-11-16 08:18:_

**AI review** of `e90162cb6b`: Throwaway PR that adds a 401-line text file solely to verify the CI diff-size gate rejects it; no code, no logic, no security or correctness concerns. No findings.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
