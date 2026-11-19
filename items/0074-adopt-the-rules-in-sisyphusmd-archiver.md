# #74 Adopt the rules in SisyphusMD/archiver

- Kind: issue, state: open, by cody, created 2026-11-17T07:54:22-08:00
- Labels: status:blocked, type:chore; milestone: none

Found auditing every SisyphusMD repo on 2026-11-17: archiver has none of the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), no nightly issue-archive and no .forgejo/RULES.md, so its required checks are its own CI only. Bring it in per docs/adopting.md (An existing repo): workflows, scripts, issue templates and labels, RULES.md copy, CONTRIBUTING.md, protection with the rules' checks proven on a PR first, annex mirror and issue-archive.

## cody, 2026-11-17T13:47:08-08:00

Starting adoption in an isolated worktree. It will use the settled main tip after archiver #348 before publication. Current Docker CI check names stay in place.

## cody, 2026-11-17T14:45:27-08:00

Archiver adoption PR archiver#351 merged at b34721c and both mirrors match. Its issue archive ran successfully. GitHub mirror lockdown is archiver#354 and the GitHub mirror credential now accepts workflow updates. Stricter protection remains open pending release conversion and check proof.

## cody, 2026-11-17T15:04:20-08:00

Archiver #354 merged at 06d756f after its exact integration checks passed. GitHub and annex match the exact Forgejo tip. GitHub Actions has only the SHA-pinned lockdown workflow active. The temporary Renovate pause was restored. Existing main protection is in place while #86 release conversion and gate proof continue.

## cody, 2026-11-17T23:57:43-08:00

Archiver #355 is merged and its guarded publish workflow rejected an ordinary merged PR in run #756. The shared required checks were proved in archiver#358. Strict adoption awaits the first approved maintenance release through the replacement path. release/0.11 still equals v0.11.7 and has no Unreleased entries. Keep archiver#357 draft until the new path is proven.

## cody, 2026-11-18T06:18:47-08:00

Retested the maintenance path from the current release/0.11 tip (caf0bb13bf8d1dfbc6f1711888bb0fb498fa4689) and current trusted main. An isolated Git primary reproduced v0.11.8, verified the exact merge, created and replayed the annotated tag, and rejected a substituted PR head. The version-only diff leaves the Docker build inputs identical to v0.11.7, and the digest-matching v0.11.7 container passed both maintenance startup smoke checks. The live branch is still at v0.11.7 with an empty Unreleased section. The first approved release of a maintenance change is still the trigger for validating hosted qualification and retirement of the old writer.
