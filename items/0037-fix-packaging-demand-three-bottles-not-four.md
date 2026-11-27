# #37 fix(packaging): demand three bottles, not four

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:33-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#27 (pull request, opened by cody on 2026-10-26, merged 2026-10-26). Branch `refs/pull/27/head` into `main`._

Homebrew stopped building Intel macOS bottles in 2026-09, so both consumers drop the `sequoia` bottle leg. `update-tap.sh` now demands 3 tags. `bottle-block.py` keeps `sequoia` in `TAG_ORDER` (ordering only, not required).
