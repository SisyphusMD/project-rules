# #10 ci: move the CI, AI review and issue-archive workflows here

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:22-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#10 (pull request, opened by cody on 2026-11-16, merged 2026-11-16). Branch `refs/pull/10/head` into `main`._

Refs #2

The CI, AI review and issue-archive workflows and their scripts were canonical in cody/agents (`skills/project-issues/template`), with a copy in bryantserver/casa. This moves them here unchanged from Casa's copy, so every repo copies from this repo. The only edits: the "Canonical copy" comments point here, and `CI` also runs on `pull_request` for this PR only, because a `pull_request_target` workflow skips the PR that adds it. The next PR removes that trigger.

`AI review` first runs on the next PR. Known gaps, each its own issue or PR: Diff size check and cross-repo issue links (#2), the reviewer reading RULES.md instead of README (#2), lint config from main (#8), tests for these scripts (#9).

No tests: moved unchanged from bryantserver/casa; their tests are #9.

## cody, 2026-11-16T14:07:22-08:00

_cody, 2026-11-16 07:31:_

Issue link fails only because it runs main's copy of issue-link.py, and main has no scripts until this PR merges (log: `can't open file '.forgejo/scripts/issue-link.py'`). Lint, Secrets and Tests with code passed. main is not protected yet; merging, then the next PR runs every gate from main and protection follows once they pass.
