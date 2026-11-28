# #147 Gate jobs fail on a PR body over 128 KB

- Kind: issue, state: closed, by cody, created 2026-11-27T08:14:39-08:00
- Labels: status:in-progress, type:bug; milestone: none

The three gate jobs (Issue link, Tests with code, Diff size) get the PR description through `PR_BODY: ${{ github.event.pull_request.body }}`. Linux refuses any single environment string over 128 KB, so a longer body makes the step fail before the script runs: `exec /usr/bin/bash: argument list too long`, exit 255.

Seen 2026-11-27 on Renovate PRs bumping uv across many releases: bodies of 181 KB and 214 KB, mostly release notes. Every repo whose Renovate PRs carry long changelogs hits it, and it blocks their automerge.

Fix: the scripts read the body from the event payload at `GITHUB_EVENT_PATH`, which the runner writes for every job, and the workflow stops passing it in the environment. `PR_BODY` stays as an override for the tests.


## cody, 2026-11-27T08:48:07-08:00

Fixed in #148, merged at fcfe0e3. The gate scripts read the PR description from the event payload; a proof run on the branch read a 138,853-byte body inside a called workflow with no PR_BODY set and passed. Next: none; the long Renovate PRs that hit this rerun on their next rebase.
