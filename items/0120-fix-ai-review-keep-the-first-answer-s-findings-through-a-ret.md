# #120 fix(ai-review): keep the first answer's findings through a retry

- Kind: pull, state: closed, by cody, created 2026-11-21T18:44:26-08:00
- Labels: none; milestone: none
- refs/pull/120/head -> main, merged: True

Closes #119

- A finding the first answer had and the retry left out is kept (the retry wins on a shared id).
- A retry cut off at its 16,000-token cap fails the check with the first answer's findings shown and a remedy, instead of an error that named the wrong cap.
- A pass after a retry says "after a retry" in its status.

Not changed, decided on #119: a clean retry after an unreadable first answer still passes (failing it would fail every clean PR whose first answer was malformed; the retry quotes the first answer and its reasoning), and a carried blocker whose file left the diff keeps blocking (downgrading it would fail open; ValidateFindings pins this).

Tests: 189 passed, 1 skipped; the new tests fail on main. This PR's own AI review is also the first live test of the pinned checkout from #58.

## forgejo-actions, 2026-11-21T18:45:20-08:00

<!-- ai-review -->
**AI review** of `1d49b9b5d4`: The PR correctly addresses issues #2 and #3 from #119: merging the first answer's findings into a successful retry (retry wins on shared id), catching CutOff on the retry with the first answer's findings preserved, and adding the 'after a retry' status note. Tests cover all new behaviours and the old test was appropriately updated for the changed exception handling. No blocking issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
