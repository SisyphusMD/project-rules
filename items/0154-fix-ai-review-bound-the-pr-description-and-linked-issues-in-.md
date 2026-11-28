# #154 fix(ai-review): bound the PR description and linked issues in the prompt

- Kind: pull, state: closed, by cody, created 2026-11-27T19:22:03-08:00
- Labels: none; milestone: none
- refs/pull/154/head -> main, merged: True

Closes #153

A Renovate group PR carried about 1 MB of release notes in its description. The review put all of it into the prompt, and the model refused the request with HTTP 400 before reviewing.

- The description is clipped to 20,000 characters, keeping its start and end, the same way each reply is clipped. Issue references are still read from the whole description, and a test holds that.
- The linked issues are capped at 40,000 characters in total. Each issue was already bounded, but the number of issues was not.
- When the model refuses a request, the check now shows the HTTP code and the start of the server's message, instead of only `HTTPError`.

`tests/test_ai_review_model.py` and `test_ai_review_context.py` pass (109 tests).


## forgejo-actions, 2026-11-27T19:22:35-08:00

<!-- ai-review -->
**AI review** of `621c24b07e`: Clean, well-scoped fix for #153: bounds the PR description and linked-issues text in the prompt, and surfaces the HTTP code and server message on a model refusal. Tests cover all three new behaviours and confirm issue references are still read from the unclipped body.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
