# #22 Move to public SisyphusMD/project-rules and retire this repo and project-standard

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:29-08:00
- Labels: status:in-progress, type:chore; milestone: none

_Recreated from bryantserver/project-rules#22 (issue, opened by cody on 2026-11-16)._

Decisions on #1 (2026-11-16). Steps: build SisyphusMD/project-rules private; first commit by hand folding in project-standard (shared/ copied byte-for-byte, since consumer locks pin SHA-256s); recreate this repo's issues and PRs with the same numbers, project-standard's after them noting old numbers, Renovate bumps as one summary; scan for secrets and names; repoint whiskerless and dreame-valetudo; make public on Cody's yes; a private repo and GitHub mirrors (GitHub on Cody's yes); bundle and export both old repos, then delete them and their mirrors (GitHub deletion on Cody's yes). Rename the project-issues skill to project-rules.

## cody, 2026-11-16T16:27:11-08:00

Status: this repo is public (2026-11-16) and tagged v0.2.0 (156f8c1). Its a private repo push mirror is live (SisyphusMD/project-rules on the house mirror host, scoped write:repository token; first sync verified). Consumers re-vendored from v0.2.0 with Renovate pointed here: SisyphusMD/whiskerless#177 and SisyphusMD/dreame-valetudo#279, CI running. The /project-rules skill (renamed from project-issues) and the group maps point here. Next: merge both consumer PRs, then retire SisyphusMD/project-standard (Forgejo, a private repo, GitHub) and bryantserver/project-rules (Forgejo, a private repo, its mirror token), each bundled and exported first. Still open: this repo's GitHub read-only mirror, after the maintainer's go-ahead.

## cody, 2026-11-16T19:37:36-08:00

Status 2026-11-16: retired. SisyphusMD/project-standard and bryantserver/project-rules are deleted on Forgejo and a private repo, with the old push-mirror token; full bundles and the issue exports are kept off-repo with restore steps. All consumers moved first: whiskerless#177, dreame-valetudo#279, appliance-job-monitor#4 (v0.2.0), and a private repo (clones this repo, retires the old checkouts on the Macs). v0.3.0 tagged after #53 and #45. Open: project-standard's GitHub copy and a GitHub read-only mirror of this repo, both waiting on the maintainer. merach-ble (local only, no remote) still vendors from v0.1.28 and moves when it is published.

## cody, 2026-11-16T22:47:24-08:00

Done 2026-11-16. project-standard's GitHub copy is deleted (it held nothing Forgejo lacked: no issues, releases or GitHub-only refs). This repo now has a read-only GitHub copy at github.com/SisyphusMD/project-rules (issues, wiki, projects and Actions off; description points here), pushed by a Forgejo SSH push mirror over ssh.github.com:443 with a write deploy key scoped to that repo; first sync matched every ref. The backup mirror also live. Nothing left on this issue.
