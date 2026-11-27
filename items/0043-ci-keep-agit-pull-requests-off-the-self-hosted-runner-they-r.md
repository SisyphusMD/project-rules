# #43 ci: keep AGit pull requests off the self-hosted runner (they report this repo as their head, so the fork gate let them through, and a maintainer's reopen runs this branch's workflows with secrets)

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:35-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#37 (pull request, opened by cody on 2026-11-16). Branch `ci/agit-pr-guard` into `main`._

Forgejo treats an AGit pull request (pushed to `refs/for/main`, no fork needed) as untrusted and holds its runs for approval, but its payload reports this repository as the head (`head.repo.full_name == github.repository`), so the existing fork gate let it through. When a maintainer acts on an outsider's PR (reopen), Forgejo 17 runs this branch's workflows, with secrets, against the PR's commit (services/actions/trust.go). Outside contributors are about to be able to sign in with GitHub and open AGit PRs, so the gate now also requires `github.event.pull_request.flow == 0`.

Proof (throwaway SisyphusMD/agit-guard-proof-20261116): an AGit PR's payload has `flow=1` and head repo = base repo, and the gated job was skipped (run 37485); a branch PR has `flow=0` and the gated job ran (run 37486).

Outside PRs get CI when a maintainer, after reading the diff, pushes the head to a branch here.

CONVENTIONS.md states the gate the same way, so new projects copy the full condition.

_Still open when project-standard was retired: its change is not in this repo. It lands here as a new pull request that closes this issue._
