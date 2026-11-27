# #125 feat(gate): run the gate scripts from project-rules main in every repo

- Kind: pull, state: closed, by cody, created 2026-11-24T17:45:06-08:00
- Labels: none; milestone: none
- refs/pull/125/head -> main, merged: True

Refs #78

Each repo runs its own copy of the gate scripts, and copies drift: two repos had stricter ones than this repo, and a fix here needs a PR in every repo. `Issue link`, `Tests with code`, `Diff size` and `AI review` now clone this repo's `main` into `/tmp/gate` and run the script from there, as decided on #78. Consumers change in their own PRs after this one.

- The clone is anonymous, runs before the PR is checked out, has no local fallback, and logs the commit it used. If it fails, the job fails.
- `AI review` sets its required status to pending before the fetch. The script used to be the first thing to set it, so a failed fetch on a re-review would have left an earlier pass in place.
- Job names are unchanged, so the required contexts still match.
- `Tests / The gate scripts can be fetched` runs the same step from the PR's own file. The gate jobs run from main, so a broken fetch would otherwise show only once it blocked every PR.

`tests/test_gate_fetch.py` rejects a gate job that skips its script or runs a local one, a fetch step that differs from the proven one, a fetch that takes another branch or passes when the repo cannot be read, and a re-review that leaves the old status. Rule 15 and `docs/adopting.md` describe the new source.


## forgejo-actions, 2026-11-24T17:46:06-08:00

<!-- ai-review -->
**AI review** of `f01ef8a3c4`: Well-scoped implementation of the #78 decision: gate jobs now clone project-rules main into /tmp/gate and run scripts from there, with a pre-fetch pending-status step in AI review, a gate-fetch proof job in tests.yml, and a thorough test file covering fetch correctness, failure propagation, re-review status handling, and step consistency. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
