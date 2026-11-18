# #84 docs: ban AI attribution in commits, PRs and comments

- Kind: pull, state: closed, by cody, created 2026-11-17T09:23:36-08:00
- Labels: none; milestone: none
- refs/pull/84/head -> main, merged: True

Closes #80

Contributions arrived with assistant co-author trailers and "Generated with" lines. Rule 9 now says commit messages and trailers, PR titles and descriptions, and issue and PR comments carry no AI attribution: no `Co-Authored-By` for an assistant, no "Generated with" line, no robot emoji, no AI tool named as an author. Whoever submits the change is its author. The required AI review's own comments and a rule 2 `Technical call:` label are not attribution. The CONTRIBUTING template points at rule 9 with one example.

It is folded into rule 9 rather than added as rule 24, because other docs and the AI review cite rules by number.

Not enforced by a check yet: the AI review can only block on diff lines and never sees commit messages. #81 tracks a CI job for it. Docs only, so no test.

## forgejo-actions, 2026-11-17T09:23:47-08:00

<!-- ai-review -->
**AI review** of `1a2fc0bc16`: Clean, well-scoped docs-only PR that folds the AI-attribution ban into rule 9 and adds a pointer in the CONTRIBUTING template, matching the recorded decision on #80. The diff is minimal, the rule text is specific about what is banned and what is exempt, and the CHANGELOG entry is appropriate.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
