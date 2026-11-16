# #40 fix(packaging): revendor-standard.sh no longer holds its output open after finishing

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:34-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#31 (pull request, opened by cody on 2026-10-26, merged 2026-10-26). Branch `refs/pull/31/head` into `main`._

Killing the watchdog subshell orphaned its `sleep`, which inherited stdout. Anything reading the output (a pipe, Renovate post-upgrade capture) waited the full 300 s clone deadline after the vendor was done. The watchdog now traps TERM and kills its own sleep, and its output goes to /dev/null. tests/test-revendor-watchdog.sh times it (old script: 30 s stall at a 30 s deadline; new: 0 s).
