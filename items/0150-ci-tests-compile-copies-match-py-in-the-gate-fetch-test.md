# #150 ci(tests): compile copies-match.py in the gate-fetch test

- Kind: pull, state: closed, by cody, created 2026-11-27T09:20:28-08:00
- Labels: none; milestone: none
- refs/pull/150/head -> main, merged: True

copies-match.py is on main since #146, so the Tests job that fetches main now compiles it with the other gate scripts. A broken main copy then fails a Tests check here before it fails Copies match in every repo.

Closes #149


## forgejo-actions, 2026-11-27T09:47:17-08:00

<!-- ai-review -->
**AI review** of `0463b16f3a`: Clean, minimal change that adds copies-match to the gate-script compile list in the Tests workflow, exactly as issue #149 specifies. The stale comment is correctly removed, the list stays alphabetical, and the CHANGELOG is updated.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
