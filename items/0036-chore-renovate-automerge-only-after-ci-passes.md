# #36 chore(renovate): automerge only after CI passes

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:32-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#21 (pull request, opened by cody on 2026-10-09, merged 2026-10-09). Branch `refs/pull/21/head` into `main`._

platformAutomerge: false, so Renovate merges an automerge PR itself once its checks are green. With platform automerge Forgejo merged immediately when main required no checks: archiver #192 (an rclone bump) merged 3 seconds after opening and broke the image build. Cody approved this change across the bryantserver and SisyphusMD repos (2026-10-09).
