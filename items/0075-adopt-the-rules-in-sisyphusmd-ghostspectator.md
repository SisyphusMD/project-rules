# #75 Adopt the rules in SisyphusMD/GhostSpectator

- Kind: issue, state: open, by cody, created 2026-11-17T07:54:23-08:00
- Labels: status:blocked, type:chore; milestone: none

Found auditing every SisyphusMD repo on 2026-11-17: GhostSpectator has none of the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), no nightly issue-archive and no .forgejo/RULES.md, so its required checks are its own CI only. Bring it in per docs/adopting.md (An existing repo): workflows, scripts, issue templates and labels, RULES.md copy, CONTRIBUTING.md, protection with the rules' checks proven on a PR first, annex mirror and issue-archive.

## cody, 2026-11-17T13:45:10-08:00

Starting adoption from verified main 938021b after #24 in an isolated worktree.

## cody, 2026-11-17T14:08:19-08:00

GhostSpectator #27 settled at 5d8aa89, its restore check is green, and the first issue archive ran and synced to the annex. GitHub rejected the workflow update because the existing mirror token lacks Workflow write. GitHub Actions remain disabled pending scoped token rotation. Full branch protection still depends on the release workflow change.

## cody, 2026-11-17T14:45:27-08:00

GitHub mirror credential rotation cleared the workflow rejection. Both mirrors match 5d8aa89 and GitHub Actions has only the SHA-pinned lockdown workflow active. Stricter protection remains open pending GhostSpectator#28 and check proof.

## cody, 2026-11-17T23:57:43-08:00

GhostSpectator #29 is merged with matching mirrors and the shared required checks were proved in GhostSpectator#30. Strict adoption awaits licensed local PEAK gameplay and an actual approved Thunderstore release through the new workflow.

## cody, 2026-11-18T06:18:48-08:00

The release-preparation regression passed, including the gameplay confirmation gate and candidate-only push. A licensed PEAK installation is available under the maintainer’s interactive account. The configured Forgejo runner is isolated from that account and GhostSpectator has no gameplay runner. The remaining gate is PatchValidator and a gameplay run using the actual candidate ZIP in the interactive game session.

## cody, 2026-11-20T17:46:35-08:00

Status unchanged: needs PatchValidator plus a gameplay run of the actual candidate ZIP in Cody's interactive PEAK session, and a separate approval for the first Thunderstore release. Not started; asked after the Archiver release.
