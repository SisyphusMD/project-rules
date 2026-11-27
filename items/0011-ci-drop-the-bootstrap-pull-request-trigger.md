# #11 ci: drop the bootstrap pull_request trigger

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:23-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#11 (pull request, opened by cody on 2026-11-16, merged 2026-11-16). Branch `refs/pull/11/head` into `main`._

Refs #2

`CI` ran on `pull_request` for #10 only, because a `pull_request_target` workflow skips the PR that adds it. This removes that trigger, so every gate runs from main's copy and a PR cannot change the check that judges it. This PR is also the first full run of every gate here, including `AI review`; main gets protected once all of them pass.

No tests: workflow trigger removal; this PR's own CI run is the proof.

## cody, 2026-11-16T14:07:23-08:00

_forgejo-actions, 2026-11-16 07:33:_

**AI review** of `d4327c72cd`: Clean removal of the bootstrap `pull_request` trigger from CI, leaving only `pull_request_target` so that PRs cannot tamper with the workflow that judges them. The change is correct, minimal, and a security improvement; the PR's own CI run serves as validation for a workflow-config change.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
