# #90 Test the AGit and fork trust gate in tests.yml, and say in CONTRIBUTING that such PRs get no CI

- Kind: issue, state: closed, by cody, created 2026-11-17T13:11:50-08:00
- Labels: status:in-progress, type:chore; milestone: none

Follow-up to the AGit gate and #79 (`pull_request` runs the PR head's workflow; AGit under a maintainer account ran CI on unreviewed code).

- Nothing tests the gate in `tests.yml`. Add a test that walks every job of every `pull_request`-triggered workflow under `.forgejo/workflows/` and fails unless its `if:` carries both `github.event.pull_request.head.repo.full_name == github.repository` and `github.event.pull_request.flow == 0`, with named exemptions and a reason for each. A job that loses its whole `if:` must fail it. `pull_request_target` workflows (`ci.yml`, `ai-review.yml`) are out of scope; that is #57.
- `CONTRIBUTING.md` and `templates/CONTRIBUTING.md` should say that AGit and fork pull requests get no CI from a repo's own test workflows, and that a maintainer re-pushes the change to a branch in the repo to run it, so repos adopting the rules carry the line.

## cody, 2026-11-17T13:24:52-08:00

Status: guard test (with a pyyaml pin in tests.yml) and the CONTRIBUTING and template note written, green locally (74 passed), not committed: needs cx review (workflow change) before commit. Branch ci/agit-guard-followups, one PR with #91.

## cody, 2026-11-17T13:48:58-08:00

Merged in #94 at 2318578 after #93. All ten Forgejo contexts passed. The regression covers a removed guard, either clause removed, and OR in place of AND. The standard template documents the maintainer branch-PR route.
