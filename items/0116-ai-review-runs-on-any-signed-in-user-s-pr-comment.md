# #116 AI review runs on any signed-in user's PR comment

- Kind: issue, state: closed, by cody, created 2026-11-21T11:31:47-08:00
- Labels: status:in-progress, type:bug; milestone: none

Since GitHub sign-up opened (a private repo), any approved account can comment on an open PR in a public repo. `ai-review.yml` runs on every `issue_comment` on a PR except the reviewer's own, so a comment from anyone starts a review on the Studio model: up to 45 minutes each, queued per PR and never cancelled. A burst of comments ties up the Studio, and each reply goes to the model as an argument it may accept to withdraw a blocking finding.

Plan: run the comment path only when the commenter can push to the repo or wrote the PR. Forgejo's Actions comment payload carries the commenter's own permission in `repository.permissions` (services/actions/notifier.go `notifyIssueCommentChange`, v17.0.2), so the gate needs no list of names. `pull_request_target` runs stay as they are; the PR author can still reply to findings. Comments from others stay visible to the model on the next allowed run, as data.

Then copy the change to the public repos that carry `ai-review.yml` (outsiders cannot see the private ones).

Requested by Cody 2026-11-21 ("yes to all") after a review of what an approved outside account can do.

## cody, 2026-11-21T11:31:56-08:00

Claude has this (session 8b0edc09).

## cody, 2026-11-21T11:50:39-08:00

Status: canonical gate merged in #117 (d33b2d1), verified on main. Copies opened unchanged in every public repo that carries the file: homebrew-tap #22, dreame-valetudo #318, whiskerless #246, archiver #380, appliance-job-monitor #28, GhostSpectator #37, each closing its own issue. Private repos keep the old copy: outside accounts cannot see them. Residual: an outside AGit PR can still start reviews through pull_request_target, recorded on #57.
