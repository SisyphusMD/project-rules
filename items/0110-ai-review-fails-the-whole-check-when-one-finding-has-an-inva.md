# #110 AI review fails the whole check when one finding has an invalid severity

- Kind: issue, state: open, by cody, created 2026-11-20T13:11:31-08:00
- Labels: status:in-progress, type:bug; milestone: none

On cody/macos#75 (2026-11-20) the AI review failed closed three times in a row on its own output, never on the diff:
- a ValueError;
- no JSON in the answer;
- `finding F5 has an invalid severity or status`.

`.forgejo/scripts/ai-review.py` (around line 243) raises on the first finding whose severity is not `blocking` or `suggestion`, so every other finding is thrown away along with the verdict and the PR stays blocked. Proposed: re-ask the model once with the validation error, and if it still fails, report the malformed finding as a blocking finding with its raw text, so the review still fails closed but the author can see and answer the findings. Includes a test that fails on today's code.

## cody, 2026-11-20T15:51:44-08:00

I have this one (Claude agent working for Cody, branch fix/110-reask-malformed-answer). Scope widened: the no-JSON answer ("no JSON object in the model's answer") that failed cody/macos#75 is covered too, not only the invalid severity/status case. Plan: on a parse or validation failure, re-ask the model once with the error; if the second answer is still bad, the check fails, the PR comment names what was malformed, and the well-formed findings are posted. Nothing malformed ever passes, and the #107 leaked-draft parsing is unchanged.

## cody, 2026-11-20T16:37:59-08:00

Technical call: an unreadable response envelope (IndexError or AttributeError from choices/message) gets the same one re-ask as a malformed answer. The house review argued a retry doubles a long generation on the shared Studio. It is kept because an empty or odd envelope is more likely transient than a bad verdict, and the retry is bounded to one, inside the same deadline. Decided by: Claude, 2026-11-20.
