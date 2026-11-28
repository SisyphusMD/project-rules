# #156 docs(rules): require Copies match

- Kind: pull, state: closed, by cody, created 2026-11-27T20:44:29-08:00
- Labels: none; milestone: none
- refs/pull/156/head -> main, merged: True

Adds `Copies match` to the required checks in rule 15, and says in adopting.md that a change to a copied file ships with its rollout to every repo, since the required check blocks PRs in a repo whose copies are behind. The check has a passing run (#150) and a real failure on a consumer PR, as step 5 asks. Protection in each repo follows after this merges.

Closes #155


## forgejo-actions, 2026-11-27T20:44:52-08:00

<!-- ai-review -->
**AI review** of `0fe8e3ff97`: Small, focused documentation change adding `Copies match` to the required-checks list in rule 15 and explaining the rollout obligation in adopting.md, consistent with the decision recorded on #155. No code changes, no test-coverage impact, diff well under 400 lines.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
