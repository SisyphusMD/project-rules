# #91 fetch-release-assets.sh comment still describes GitHub runners

- Kind: issue, state: closed, by cody, created 2026-11-17T13:11:51-08:00
- Labels: status:in-progress, type:chore; milestone: none

The header comment of `shared/packaging/fetch-release-assets.sh` still describes the split CI: "amd64 here, arm64 and macOS on GitHub", "the NAS, which no GitHub runner can reach", and "Half of these assets come from the mirrored-tag workflows". Every SisyphusMD job now runs on Forgejo runners and GitHub is a read-only mirror. The release page is still the rendezvous, because the amd64, arm64 and macOS halves are built by separate workflows on separate runners.

Correct the comment for v0.3.1. Comment only; no behaviour change.

## cody, 2026-11-17T13:24:52-08:00

Status: comment fix written in the same worktree as #90, not committed yet (review pending). Comment only; shellcheck clean.

## cody, 2026-11-17T13:34:49-08:00

The review found the same retired two-forge runner split in wait-for-release.sh. This issue will correct both release-helper comments. The shell logic stays byte-for-byte identical.

## cody, 2026-11-17T13:45:44-08:00

The caller audit confirmed the NAS bottle refresh and native arm64 workflow. The same cutover wording is stale in the PyPI readiness, registry and prune comments. This PR will correct those related comments for v0.3.1 as well. The vendored runtime logic is unchanged.

## cody, 2026-11-17T13:47:32-08:00

Merged in #93 at f4d070c. All ten Forgejo contexts passed. Comment-only edits in five shared release helpers, for the v0.3.1 vendoring update.
