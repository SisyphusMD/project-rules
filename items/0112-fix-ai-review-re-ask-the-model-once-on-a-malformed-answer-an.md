# #112 fix(ai-review): re-ask the model once on a malformed answer and post the usable findings

- Kind: pull, state: closed, by cody, created 2026-11-20T16:11:57-08:00
- Labels: none; milestone: none
- refs/pull/112/head -> main, merged: True

Closes #110

On a private repo the required AI review failed closed three times on the model's own output (a ValueError, an answer with no JSON, `finding F5 has an invalid severity or status`). The first malformed finding raised and the whole review, including every good finding, was thrown away.

Now a parse or validation failure puts the same prompt back to the model once, with the error (and the rejected answer when there was one). If the second answer is still bad the check fails, the comment gains a "Malformed model output" section naming each problem (the finding's raw text, or both errors when no JSON came back twice), and the well-formed findings and earlier findings are still posted and kept in the state. A malformed answer never produces success. The `</think>` parsing from #107 is untouched: a draft with no final verdict still raises, now twice, and fails.

Tests (new ones fail on main's script: the retry never happens, the comment is never posted, `validate` has no `lenient`): invalid severity then valid, no JSON then valid, malformed twice, no JSON twice with earlier findings kept, wrong-shape second answer, non-string id, missing id, a leaked draft that never passes, a retry that hits the token cap keeps the `error` status.


## forgejo-actions, 2026-11-20T16:18:45-08:00

<!-- ai-review -->
**AI review** of `c05476c8d9`: Clean, well-scoped fix for #110: the AI review now re-asks the model once on a malformed answer, posts usable findings even when the second answer is still bad, and fails closed. The validate/get_result/render/main changes are correct, the id-validation tightening is intentional, and the test suite covers every listed scenario including the leaked-draft and CutOff paths.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
