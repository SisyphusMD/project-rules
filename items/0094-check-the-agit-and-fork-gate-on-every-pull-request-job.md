# #94 Check the AGit and fork gate on every pull-request job

- Kind: pull, state: closed, by cody, created 2026-11-17T13:47:22-08:00
- Labels: none; milestone: none
- refs/pull/94/head -> main, merged: True

Closes #90

The standard's test suite now checks each job in every `pull_request` workflow for both trust clauses. The regression fixture detects absent conditions, either clause missing, and conditions that join the clauses with OR. A positive control checks that the existing Tests jobs were inspected.

The local and template CONTRIBUTING guides explain how a maintainer runs the full suite on a branch PR after reading an AGit or fork submission.


## forgejo-actions, 2026-11-17T13:47:52-08:00

<!-- ai-review -->
**AI review** of `3841728c66`: The PR adds a guard test that walks every pull_request-triggered workflow and asserts each job carries both the fork and AGit trust clauses, with a regression fixture covering absent/partial/OR-joined conditions, plus the CONTRIBUTING and template notes the issue asked for. The logic, normalization, and positive/negative controls are sound; no blocking issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
