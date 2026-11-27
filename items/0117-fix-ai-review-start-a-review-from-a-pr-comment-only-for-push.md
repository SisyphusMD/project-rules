# #117 fix(ai-review): start a review from a PR comment only for pushers and the PR author

- Kind: pull, state: closed, by cody, created 2026-11-21T11:45:44-08:00
- Labels: none; milestone: none
- refs/pull/117/head -> main, merged: True

Closes #116

Since GitHub sign-up opened, any approved account can comment on an open PR in a public repo, and every such comment started an AI review: up to 45 minutes on the Studio model each, queued per PR and never cancelled. The comment path now runs only when the commenter can push to the repo or wrote the PR. `pull_request_target` runs are unchanged.

The gate reads `github.event.repository.permissions.push`, which Forgejo fills with the commenter's own permission (services/actions/notifier.go `notifyIssueCommentChange`, v17.0.2). Checked against stored run payloads on this instance: cody's comments carry `admin:true,push:true`, babysitter's, fixer's and renovate's `admin:false,push:true`, so the bots' replies still start reviews.

The new test evaluates the job's own `if:` against comment payloads. It rejects an outside account's comment, which the old condition let through (1 of 7 cases failed on main's file), and checks that a payload without `repository.permissions` falls back to the PR author only.

Still open, not in this PR: an outside AGit PR can still start reviews through `pull_request_target` (opened/edited/synchronize); that belongs to #57. Copies in the public repos follow per #116.


## forgejo-actions, 2026-11-21T11:48:30-08:00

<!-- ai-review -->
**AI review** of `f693b576ec`: Clean, focused fix for #116: the comment-triggered AI review path now requires the commenter to have push permission or be the PR author, with a well-structured test that evaluates the real workflow condition against Forgejo-shaped payloads and proves the old condition was open.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
