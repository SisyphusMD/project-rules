# #130 feat(gate): make ci.yml and ai-review.yml callers of the shared workflows

- Kind: pull, state: closed, by cody, created 2026-11-25T21:26:40-08:00
- Labels: none; milestone: none
- refs/pull/130/head -> main, merged: True

Refs #78

Repos copy this repo's `ci.yml` and `ai-review.yml`, so every repo carried the gate and AI review jobs, and copies drift. Both files now only call `gate.yml`, `gate-lint.yml` and `review.yml` from main (#129). They keep what a called workflow cannot hold: the triggers, the concurrency groups and the one secret the jobs may see, `ISSUE_READ_TOKEN`, handed over by name and never with `secrets: inherit`.

Proven first in homebrew-tap (homebrew-tap#34, proof PR homebrew-tap#35, closed unmerged). With no issue named, `CI / Issue link (pull_request_target)` failed. Once the description named one, every required check passed under its usual name, and a maintainer reply re-ran the review through the called job. Each calling job adds one check of its own (`CI / shared-gate`, `CI / shared-lint`, `AI review / shared-review`); adopting.md now says never to require those, since one passes when the jobs it calls are skipped.

The tests move from the copied jobs to the callers. They now check the callers point at main with only the issue reader handed over, keep their triggers and concurrency, and never take a required check's name. The fork guard and trigger-rule tests stay on the called files. adopting.md also covers a repo that keeps its own Lint and Secrets, and says that project-rules main now runs as trusted code in every calling repo. `.renovaterc.json` and an `ai-review.py` comment named `ci.yml` and `ai-review.yml` for what now lives in `gate-lint.yml` and `review.yml`.

This PR is judged by main's old copies, and the next one here runs on the callers.


## forgejo-actions, 2026-11-25T21:27:12-08:00

<!-- ai-review -->
**AI review** of `e98f1a8fe6`: Clean, well-scoped PR that turns ci.yml and ai-review.yml into thin callers of the shared workflows landed in #129. Tests, docs, changelog, and cross-references are all updated consistently. No correctness, security, or coverage issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
