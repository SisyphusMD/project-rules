# #41 fix(triage): retry a job no runner ever took

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:34-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#35 (pull request, opened by cody on 2026-11-13, merged 2026-11-13). Branch `refs/pull/35/head` into `main`._

GitHub cancels a macOS arm64 job it cannot place after 15 minutes ("not acquired by Runner"). It ends `cancelled`, which the triage treated as a veto, so whiskerless rc.74 and rc.75 sat red until rerun by hand. This adds that class with exact evidence (no steps, no runner, GitHub annotation), and lets it alone retry up to attempt 5.
