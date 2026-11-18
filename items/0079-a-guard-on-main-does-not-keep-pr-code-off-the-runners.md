# #79 A guard on main does not keep PR code off the runners

- Kind: issue, state: open, by cody, created 2026-11-17T08:58:47-08:00
- Labels: status:needs-decision, type:bug; milestone: none

On 2026-11-17 three outside pull requests moved from GitHub (whiskerless #188-#190) ran unreviewed code on the runners for up to two minutes, until cancelled. No secret was exposed: the only job holding one (macos, GH_REPO_READ_PAT) waits on every other job, and none finished.

Two causes:
1. A `pull_request` run uses the workflow files from the PR's head commit. The flow == 0 / same-repo guard (#46) is on main, but these PRs are based on an older main (b59ac5f2) without it, so the guard never applied. Any PR based on an old enough commit, or one that edits the workflow, bypasses a guard that lives only in workflow files.
2. The PRs were pushed as AGit under the maintainer's account, so Forgejo treated them as trusted and ran CI straight away.

Options to decide:
- Run untrusted-capable jobs only from `pull_request_target` (workflow from main, PR checked out as data), as the gate ci.yml already does, and keep `pull_request` jobs for same-repo branches pushed by maintainers.
- Use Forgejo's approval for workflows from outside contributors, if the instance supports it for AGit.
- Add a procedure to adopting.md and CONTRIBUTING: an outside PR is moved in by rebasing onto current main (so it carries the current guard) or pushed in a way that never starts CI, never as an AGit push under a maintainer account.

Also check what the automatic job token can do on a `pull_request` run from an AGit PR.
