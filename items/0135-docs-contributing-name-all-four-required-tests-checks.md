# #135 docs(contributing): name all four required Tests checks

- Kind: pull, state: closed, by cody, created 2026-11-26T09:18:11-08:00
- Labels: none; milestone: none
- refs/pull/135/head -> main, merged: True

Closes #132

main's protection now requires the four `Tests / ... (pull_request)` checks as well (Cody's decision on #132), since every repo runs the gate from this main. CONTRIBUTING.md's required-checks section left out the gate-fetch job and now says what the requirement covers: a branch pull request; AGit and fork pull requests skip those jobs and go through the maintainer flow.

This PR is the first judged with the Tests checks required.

No tests: docs only.

## forgejo-actions, 2026-11-26T09:18:31-08:00

<!-- ai-review -->
**AI review** of `e911537752`: Clean documentation-only update to CONTRIBUTING.md and CHANGELOG.md that accurately reflects the decision from #132 to require all four Tests checks on main. The diff is minimal, correctly names all four checks in prose, explains the AGit/fork exception, and the 'No tests: docs only' justification holds since no code is changed.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
