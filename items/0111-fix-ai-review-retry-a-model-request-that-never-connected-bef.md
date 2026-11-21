# #111 fix(ai-review): retry a model request that never connected before failing closed

- Kind: pull, state: closed, by cody, created 2026-11-20T15:36:14-08:00
- Labels: none; milestone: none
- refs/pull/111/head -> main, merged: True

Closes #109.

The root cause of the repeated failures was annex's runner lacking a route to the LLM, fixed in bryantserver/annex#89. This adds the bounded retry the issue proposed for real blips:

- `open_model` retries only a request that never reached the server: `URLError` whose reason is a `socket.gaierror` or an `OSError` with `ECONNREFUSED`, `EHOSTUNREACH`, `ENETUNREACH` or `ENETDOWN`. It waits 5, 15 and 30 s (about a minute in all), then makes one last attempt and fails closed as before. Timeouts, `HTTPError` and response-read errors are never retried, so a review cannot run twice. `MODEL_DEADLINE` still bounds the whole call.
- Tests: a lookup failure followed by success yields a verdict, re-sends the same prompt and logs the retry; refused and unroutable connections are retried; the retries are bounded and fail closed; timeouts, HTTP errors and a reset connection fail at once.
- CHANGELOG under `[Unreleased]`.

Checked: ruff at CI's pin; `tests.test_ai_review_model` and `tests.test_ai_review_context` (two unrelated release tests load only under pytest, same on main). qx review: findings taken (wider unsent-errno set, asserts on the log line and the re-sent body, CHANGELOG, one timeout constant); its note that the patched `time.sleep` is process-wide needs no change, as it said itself.

Repos carry copies of this script; they pick this up when they next copy it.

## forgejo-actions, 2026-11-20T15:36:56-08:00

<!-- ai-review -->
**AI review** of `d9e5a64687`: Clean, well-scoped retry for transient connection failures in the AI review gate. The retry logic correctly limits itself to errors that prove nothing was sent, the tests cover the important paths (retry-then-succeed, bounded exhaustion, non-retryable errors), and the code still fails closed. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
