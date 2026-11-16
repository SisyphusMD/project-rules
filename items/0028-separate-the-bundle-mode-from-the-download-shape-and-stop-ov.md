# #28 Separate the bundle mode from the download shape, and stop overclaiming the Linux mode

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:30-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#7 (pull request, opened by cody on 2026-08-24, merged 2026-08-25). Branch `refs/pull/7/head` into `main`._

This entry merged two decisions, and the merge produced confident wrong answers — twice in one session, from me.

**Decision 1, the bundle mode:** invisible in packaged channels, visible at runtime. macOS onefile is platform-driven (one Mach-O to codesign per frozen app, not an executable plus every `.so`; notarization acts on the `.pkg` either way, so it is not the reason). Linux onedir is **not** platform-driven and the entry now says so.

**Decision 2, the standalone download shape:** whiskerless ships a bare binary, dreame a tarball, because dreame's download must carry `dreame-fastboot` and `sunxi-fel`.

Two rationales were retired for not surviving scrutiny: that helpers require onedir (macOS ships the same helpers beside a onefile app) and that dreame pays the unpack repeatedly (it pays it twice at start, then once per human rejoin — bounded, not recurring). What remains is one real property — onefile cannot run where `TMPDIR` is `noexec` — and the honest reason to leave it alone: not churning a shipped artifact.
