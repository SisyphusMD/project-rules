# #22 Move to public SisyphusMD/project-rules and retire this repo and project-standard

- Kind: issue, state: open, by cody, created 2026-11-16T14:07:29-08:00
- Labels: status:in-progress, type:chore; milestone: none

_Recreated from bryantserver/project-rules#22 (issue, opened by cody on 2026-11-16)._

Decisions on #1 (2026-11-16). Steps: build SisyphusMD/project-rules private; first commit by hand folding in project-standard (shared/ copied byte-for-byte, since consumer locks pin SHA-256s); recreate this repo's issues and PRs with the same numbers, project-standard's after them noting old numbers, Renovate bumps as one summary; scan for secrets and names; repoint whiskerless and dreame-valetudo; make public on Cody's yes; annex and GitHub mirrors (GitHub on Cody's yes); bundle and export both old repos, then delete them and their mirrors (GitHub deletion on Cody's yes). Rename the project-issues skill to project-rules.
