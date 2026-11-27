# #129 feat(gate): add shared gate and AI review workflows for repos to call

- Kind: pull, state: closed, by cody, created 2026-11-25T15:40:32-08:00
- Labels: none; milestone: none
- refs/pull/129/head -> main, merged: True

Refs #78

Every repo carries its own copy of `ci.yml` and `ai-review.yml`, and copies drift. This adds `gate.yml` (Issue link, Tests with code, Diff size), `gate-lint.yml` (Lint, Secrets) and `review.yml` (the AI review job) as `workflow_call` workflows for repos to call from main. Nothing calls them yet. A pilot repo switches next, is proven with one failing and one passing PR, and only then do the other repos' `ci.yml` and `ai-review.yml` become small callers.

Probed on this Forgejo (17.0.2) with a throwaway repo before writing this:
- Called jobs keep their check names, `CI / Issue link (pull_request_target)` and so on, plus one extra check for the calling job, which no rule requires.
- `github.event` is the caller's payload, but `github.event_name` reads `workflow_call`, so the review job's rule tests for the `pull_request` payload instead.
- A caller can hand over one named secret, and the called file sees only that one. `workflow_call` itself may not declare secrets: Forgejo rejects the whole file.
- Concurrency in a called file is ignored, so the callers keep it.
- A missing ref or a broken called file fails the caller's run with one visible failure.

The jobs are the copied ones byte for byte (a test holds that), with one addition: checkout v7.0.1 refuses a fork's PR head only when the event is `pull_request_target`, and in a called file it is `workflow_call`, so the four jobs that check out the PR head now apply checkout's rule in a step of their own. A test runs that step against a fork, a same-repo PR and a payload without a head repo.

Large diff: the three files are the existing jobs moved out of `ci.yml` and `ai-review.yml`, which stay until the switch; the rest is tests.


## forgejo-actions, 2026-11-25T15:41:32-08:00

<!-- ai-review -->
**AI review** of `bbd3800d00`: Three new `workflow_call` workflows (`gate.yml`, `gate-lint.yml`, `review.yml`) extract the gate and AI-review jobs so repos can call them instead of carrying copies. The jobs are byte-for-byte identical to the existing ones (verified by tests) except for the fork guard and the review trigger condition, both of which are tested. Security model is sound: fork guard before any PR-head checkout, allowlists from base SHA, `-I` isolation flags, no PR code in the review checkout.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
