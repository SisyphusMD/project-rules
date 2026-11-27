# #23 Re-vendor the standard when Renovate moves the pin

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:29-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#2 (pull request, opened by cody on 2026-08-23, merged 2026-08-23). Branch `refs/pull/2/head` into `main`._

Renovate can raise `PROJECT_STANDARD` but cannot fetch the tag it then names, so every standard bump landed red and was closed as obsolete.

- `revendor-standard.sh` reads the pin, clones that tag (bounded three ways) and runs its `vendor.py`
- `vendor.py` now retires files the standard stopped shipping, and replaces by rename so a script can update itself mid-run
- `CONVENTIONS.md` corrected: the pinned Renovate image does carry python3 (verified 3.12.3 against the digest), but a script must check rather than assume
