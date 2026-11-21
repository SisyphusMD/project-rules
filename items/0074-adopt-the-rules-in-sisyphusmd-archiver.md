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

## cody, 2026-11-20T17:46:35-08:00

Decision: Yes to all: cut public Archiver v0.11.8 (Debian base refresh, archiver#371 on release/0.11) through the trusted-main Prepare/Publish Release path. Why: The first real maintenance change exercises hosted qualification and lets the old 0.11 writer retire (#357/#356).

Decided by: Cody, 2026-11-20.

## cody, 2026-11-20T17:46:35-08:00

Status (session rotating): archiver#371 merged into release/0.11 at 8fb87e1; no v0.11.8 tag yet. Cody approved the release 2026-11-20. Next: dispatch Prepare Release from main (target release/0.11, patch bump, release issue archiver#370 or a new release issue), merge the release PR while up to date, dispatch Publish Release with that PR number, verify tag, image digest, hosted qualification and both mirrors; then un-draft and merge archiver#357, close archiver#356, update this issue and #86. No holds or crons running.

## cody, 2026-11-20T18:16:13-08:00

Status: v0.11.8 tagged but NOT published. Prepare Release (run 849) qualified and opened #373; merged into release/0.11 at efe35ce (ancestry verified); Publish Release (run 851) created annotated tag v0.11.8, already on forgejo.lan and GitHub. The tag publish (run 41501) failed at the cluster skopeo push, before any image push: release/0.11 docker-publish.yml still uses the retired *.nas mirror names, and its skopeo v1.22.3 digest is gone upstream. Rerun failed the same way. ghcr has no 0.11.8; 0.11 and 0.11.7 still point at sha256:83723fb6. Fix: archiver#374 / PR #375 (.lan names + main's skopeo v1.24.1 pin). The tag is not moved (already mirrored). Proposed next: merge #375 and cut v0.11.9 with the same image contents; pending Cody. archiver#357 stays draft until a 0.11 publish succeeds.

## cody, 2026-11-20T18:21:05-08:00

Decision: Yes: merge archiver#375 and cut v0.11.9 (same image contents as the unpublished v0.11.8) through the trusted-main Prepare/Publish Release path. Why: the v0.11.8 tag is already mirrored and must not move, and its publish workflow cannot run.

Decided by: Cody, 2026-11-20.

## cody, 2026-11-20T18:52:21-08:00

Status: the maintenance release path is proven end to end. v0.11.9 (Debian base refresh) went Prepare Release run 858 -> PR #376 merged at 17cd5e1 -> Publish Release run 41557 -> tag publish run 41558, all green. Image sha256:5e6b551c on ghcr (0.11.9 and 0.11), cluster and NAS registries; release pages on Forgejo, forgejo.lan and GitHub; release/0.11 at e79fc62 on both mirrors. v0.11.8 is a tag without an image (its 0.11 publish workflow used the retired *.nas names; fixed by archiver#375, noted in the 0.11.9 CHANGELOG). The old 0.11 writer is retired (archiver#357 merged, #356 closed); merged branches deleted and mirrors synced. New bug archiver#377: Publish Release matched the qualification URL against the runner's server URL, so one attempt on a public-URL runner refused a qualified PR (rerun passed). Remaining for this issue: strict protection (the rules' standard checks and no direct pushes on main, protection for release/0.11), pending Cody's yes; #377 first.
