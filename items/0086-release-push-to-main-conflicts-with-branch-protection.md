# #86 Release push to main conflicts with branch protection

- Kind: issue, state: open, by cody, created 2026-11-17T11:12:31-08:00
- Labels: status:blocked, type:bug; milestone: none

`shared/packaging/push-tag.sh` (vendored into every repo) pushes the changelog-promotion commit straight to `main` and the tag in one atomic push. Rule 18 protects `main` with no direct pushes, admins included, so once a repo protects `main` its Release workflow fails, and the atomic push drops the tag with it. Found by review while adopting appliance-job-monitor (#73).

Fix without a bypass for the release credential: promote `[Unreleased]` through a PR, then tag the merged commit. Repos must not enable protection until this lands, or releases break.

## cody, 2026-11-17T13:56:46-08:00

Decision: Use the same two-step release flow across the house repositories: merge the release-preparation PR, then have a maintainer dispatch publishing for that exact merged release. Why: Branch protection can stay enforced and the maintainer chooses when artifacts start publishing.

Decided by: Cody, 2026-11-17.

## cody, 2026-11-17T13:56:46-08:00

Starting with the shared release contract and local tests. Existing release callers keep their current behavior until each repository switches to the two-step flow.

## cody, 2026-11-17T14:19:46-08:00

Shared verifier and tag-only push helper merged in #95 at b79dcc0 and both mirrors match. Downstream conversions are tracked in appliance-job-monitor #14, dreame-valetudo #297, whiskerless #214, Archiver #352, GhostSpectator #28 and homebrew-tap #3. Appliance is the first workflow draft. Version preparation is #97. No stricter main protection has been enabled.

## cody, 2026-11-17T15:08:40-08:00

Published annotated v0.3.1 from exact #98 merge commit 4c65c00350872d5243c5438fa7c07c5fea5d47bb. Verified the same tag object and peeled commit on Forgejo primary, annex and GitHub. All three Tests jobs passed on the tag (run #178). Appliance #14 is vendoring this release.

## cody, 2026-11-17T15:13:50-08:00

Appliance #15 settled at 2009c05, exact reviewed head 81c917c. Both mirrors match. The local workflow fixture proved tag-only publication at the verified merge after main moved, and hosted PR CI passed. The first hosted release and appliance-job-monitor #5 check-failure proof precede protective rule changes.

## cody, 2026-11-17T15:27:12-08:00

Appliance v0.1.1 completed the first live two-step release. Release issue appliance-job-monitor#16 has the exact commit, CI runs and three-host asset verification. Other release implementations remain tracked separately.

## cody, 2026-11-17T19:48:14-08:00

Rollout status: Release proof is complete in appliance-job-monitor v0.1.1 and project-rules v0.3.1. Dreame #301, Whiskerless #223 and GhostSpectator #29 merged with matching mirrors, and a hosted negative dispatch in each verified that an ordinary merged PR cannot trigger a release tag. The shared exact-candidate verifier merged in project-rules #100. The Tap foundation in homebrew-tap #8 merged, and Tap draft #12 verified all negative checks. The Tap replay follow-up #11 must settle before the sibling publisher changes pin it. Archiver #355 passed native integration and trust checks but still needs a valid hosted AI verdict; keep maintenance retirement draft #357 on hold pending live maintenance proof. Production release proof for the remaining repos and the corresponding strict protection settings remain open.

## cody, 2026-11-17T20:46:45-08:00

Release-workflow code rollout is settled. Dreame publisher #303, Whiskerless publisher #227, GhostSpectator #29, homebrew-tap #8 and #11, and Archiver #355 all merged with verified Forgejo and mirror tips. Archiver run #756 joined the hosted checks that refuse ordinary merged PRs. The failing required-check proof drafts in all five additional repos have documented exact results and are closed.

Blocked on live proof before extending strict main protection: homebrew-tap #3 awaits approved Dreame v0.3.0-rc.52 and Whiskerless v0.2.0-rc.78, GhostSpectator needs local licensed PEAK gameplay, and Archiver #357 awaits the replacement maintenance-release proof. Appliance v0.1.1 remains the complete live release and protection proof.

## cody, 2026-11-17T23:57:43-08:00

Live Homebrew publisher proof is complete for Dreame v0.3.0-rc.52 and Whiskerless v0.2.0-rc.78. Their source and bottle PRs all merged, both install matrices poured the published bottles, and main now has strict verified protection in both source repos and the tap. The results are in homebrew-tap#3 and homebrew-tap#9. Appliance and project-rules already have verified strict protection.

Remaining triggers: Archiver needs an approved release with a real maintenance change on release/0.11. The channel still points at v0.11.7 with an empty Unreleased section. Keep archiver#357 draft until the replacement release publishes and is verified. GhostSpectator needs licensed local PEAK gameplay before the first live Thunderstore release through the new workflow. Keep #74, #75 and this issue open until those proofs allow strict protection.

## cody, 2026-11-18T06:18:48-08:00

Follow-up on the two remaining release blocks: Archiver maintenance promotion, exact merge verification, tag replay and runtime smoke passed in isolation. See #74 for the remaining live-patch trigger. GhostSpectator release-preparation regression is green, and actual licensed gameplay still requires the maintainer’s interactive game environment. See #75. This follow-up did not publish a release or change branch protection.

## cody, 2026-11-20T17:46:35-08:00

Status: the Archiver maintenance trigger now exists (archiver#371 on release/0.11) and Cody approved v0.11.8 on 2026-11-20; the release run is next in a fresh session. See #74.

## cody, 2026-11-20T18:52:22-08:00

Status: Archiver now releases through merged PRs on both lines (main and release/0.11), verified by v0.11.9 (archiver#376, runs 858/41557/41558). Strict protection on archiver is the remaining step, tracked in #74. GhostSpectator (#75) is still open.
