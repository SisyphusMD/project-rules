# #32 test(release): build assertion status explicitly instead of reading it from a condition

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:31-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#12 (pull request, opened by cody on 2026-08-29, merged 2026-08-29). Branch `refs/pull/12/head` into `main`._

`$?` taken directly after a `[ ]`/`[[ ]]` is the condition's status, which shellcheck flags as SC2319 and which any command inserted before the read would silently replace. Builds `rc` explicitly instead.

This is what has been failing the Shell scripts job on main, so it blocks #10 and #11.
