# #108 AI review: 40-minute deadline inside a 45-minute job so a slow review fails with a status

- Kind: pull, state: closed, by cody, created 2026-11-19T17:35:30-08:00
- Labels: none; milestone: none
- refs/pull/108/head -> main, merged: True

Closes #55

Cody approved raising the AI review job limit from 20 to 45 minutes, with a 40-minute deadline. Reviews at the 40,000-token cap outlasted 20 minutes and were killed with the required check left pending (casa #81, cody/macos #63).

- One SIGALRM deadline covers the review from the script start through the comment write (decision on #55). urlopen's 900 s timeout only bounds each socket read, which is why it never fired.
- `MODEL_DEADLINE_SECONDS` can only shorten it, so it always stays under the job limit.
- `Deadline` is not an OSError, so urllib cannot wrap it in a URLError while connecting.
- Any unexpected error, including a bad response to the comment write, sets an error status. A final status that cannot be set fails the job.
- `timeout-minutes: 45` in ai-review.yml.

Tests cover a slow model hitting the deadline, time already spent counting against it, the cap on the override, a deadline during the comment write, a bad comment response, an unexpected error, and a failed final status.

This PR's own review runs main's 20-minute job, so it may also be killed before it answers.

## forgejo-actions, 2026-11-19T17:38:59-08:00

<!-- ai-review -->
**AI review** of `9369e1a5f8`: Clean, well-tested fix for the stuck-pending AI review check: a SIGALRM-based 40-minute deadline from script start, a 45-minute job timeout, a broad `except Exception` that always sets an error status, and a guarded final status write. Tests cover every new path (deadline hit, deadline during comment write, bad comment response, unexpected error, failed final status, override cap, alarm cancellation ordering). No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
