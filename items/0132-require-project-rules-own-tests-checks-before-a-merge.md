# #132 Require project-rules' own Tests checks before a merge

- Kind: issue, state: closed, by cody, created 2026-11-25T22:21:35-08:00
- Labels: status:needs-decision, type:decision; milestone: none

Since #78, every house repo runs Issue link, Tests with code, Diff size, Lint, Secrets and the AI review from this repo's main (gate.yml, gate-lint.yml, review.yml). main's protection here requires the CI and AI review contexts but not the Tests workflow (Tests / Lint and test the standard's own code, The gate scripts can be fetched, Shell scripts, The standard can actually be vendored), so a PR whose tests fail can still merge, and a broken shared file then fails every calling repo's next PR.

Proposal: add the four Tests / ... (pull_request) contexts to main's required checks. Claude recommends yes; the cost is that a flaky test here blocks a rules merge until it is fixed.

Waiting on Cody's yes or no.

## cody, 2026-11-26T09:00:51-08:00

Decision: yes: require project-rules' own Tests checks before a merge. Why: a PR with failing tests could merge here and break every repo that calls the shared workflows.

Decided by: Cody, 2026-11-26.

## cody, 2026-11-26T09:50:19-08:00

Applied: main's protection now requires the four Tests / ... (pull_request) checks (verified in the protection rule; main's own Tests runs are green). #135 updates CONTRIBUTING.md to match; its checks are re-running after a merge from main (CHANGELOG conflict with #138, both lines kept, 287 tests pass locally). Next: merge #135 once green, which closes this. A session working on #134 also merges into project-rules, so coordinate with it first. Handing over to a fresh Claude session.

## cody, 2026-11-26T09:55:24-08:00

Status: #135 merged at b343dd7 and verified on main (head e911537 is an ancestor); branch and worktree removed. Nothing left here.
