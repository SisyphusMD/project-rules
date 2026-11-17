# #46 ci: keep AGit pull requests off the self-hosted runner (they report this repo as their head, so the fork gate let them through, and a maintainer's reopen runs this branch's workflows with secrets)

- Kind: pull, state: closed, by cody, created 2026-11-16T14:09:07-08:00
- Labels: none; milestone: none
- refs/pull/46/head -> main, merged: True

Closes #43

Re-lands SisyphusMD/project-standard#37 here.

Forgejo treats an AGit pull request (pushed to `refs/for/main`, no fork needed) as untrusted and holds its runs for approval, but its payload reports this repository as the head (`head.repo.full_name == github.repository`), so the fork gate in `Tests` let it through. When a maintainer acts on an outsider's PR (reopen), Forgejo 17 runs the base branch's workflows, with secrets, against the PR's commit (services/actions/trust.go). Outside contributors are about to be able to sign in with GitHub and open AGit PRs, so the gate now also requires `github.event.pull_request.flow == 0`.

Proof on a throwaway private repo: an AGit PR's payload had `flow=1` with head repo = base repo, and the gated job was skipped on both open and reopen; a branch PR had `flow=0` and the gated job ran.

conventions/shell-and-workflows.md states the gate the same way, so new projects copy the full condition. Only CI config and docs change, so no tests are added; actionlint and the Lint job's yamllint pass locally.

## forgejo-actions, 2026-11-16T14:11:34-08:00

<!-- ai-review -->
**AI review** of `71f9c9a878`: Focused security fix adding `flow == 0` to the fork gate in all three jobs of the Tests workflow, preventing AGit PRs (which report the base repo as their head) from running on the self-hosted runner with secrets. Documentation in conventions is updated to match. The fix is correct, properly parenthesized, scoped to the issue, and the CI-config change is appropriately validated by the author's proof on a throwaway repo rather than unit tests.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
