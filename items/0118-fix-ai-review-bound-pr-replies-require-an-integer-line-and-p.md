# #118 fix(ai-review): bound PR replies, require an integer line and pin the checkout to the base commit

- Kind: pull, state: closed, by cody, created 2026-11-21T17:22:48-08:00
- Labels: none; milestone: none
- refs/pull/118/head -> main, merged: True

Closes #58.

- Replies on the PR are bounded like the rest of the prompt: each kept to its start and end (`clip`, 4,000 chars), newest first within 30,000, with a note naming how many older ones were dropped.
- A blocking finding's `line` must be an exact `int`: JSON `true` is a Python int and used to pass. A blocker carried over from saved state is held to the same check. `ANSWER_SCHEMA` already says `integer`, and a test pins that.
- `ai-review.yml` checks out `ref: ${{ github.sha }}` with `persist-credentials: false`. Evidence that `github.sha` is main's commit for both events: run 41970 (`pull_request_target`) fetched 4e3f968 and run 39899 (`issue_comment`) fetched 699f6bd, both main commits, and both were the old default. A depth-1 fetch of a non-tip main commit by raw SHA works on this Forgejo (17.0.2). The script uses only `TOKEN`, never git credentials.
- The workflow passes `BOT_LOGIN` itself. A test holds it equal to the login the job condition skips and to the script's default, read from source so an ambient `BOT_LOGIN` cannot mask a typo.

Not done, by decision:
- Workflow `permissions:`: not added. Forgejo reportedly ignores the key with a warning (an outside report, not yet verified on 17.0.2), and a wrongly scoped token would break the required check in every repo.
- Renovate markers on checkout pins: already met. The pins carry `# vX.Y.Z` comments, which Renovate's github-actions manager reads.
- Stale status on a closed PR: left as is. A closed PR cannot merge, and reopening it re-runs the review.

Tests: 184 passed, 1 skipped, at CI's pinned pytest and ruff, including with `BOT_LOGIN` set. Removing the `bound_replies` call makes the new `main()` test fail. Reviewed with qx and cx, and their findings were applied (start-and-end clip, the carried-over line check, the ambient-env test, the comment wording).

After merge: confirm the new checkout step on one `pull_request_target` run and one reply-triggered run, then hand both `ai-review.yml` edits to #113 as targeted changes.


## forgejo-actions, 2026-11-21T17:23:27-08:00

<!-- ai-review -->
**AI review** of `c59d4e61de`: Clean, well-scoped PR: bounds PR replies in the prompt, tightens the blocking-finding line check to reject bools (including carried-over findings), pins the checkout ref and disables credential persistence, and adds explicit BOT_LOGIN to the workflow. Tests cover each change including the integration path through main() and the workflow file itself.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->

## cody, 2026-11-21T17:24:46-08:00

Merged 0e929cc. This comment is a live check of the new pinned checkout on the reply path; the review exits at once because the PR is closed.
