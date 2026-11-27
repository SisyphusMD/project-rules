# #122 fix(ai-review): retry an answer cut off while still reasoning under the schema

- Kind: pull, state: closed, by cody, created 2026-11-22T17:28:08-08:00
- Labels: none; milestone: none
- refs/pull/122/head -> main, merged: True

Closes #121

a private repo (+296/-30) failed the AI review three times. Each time qwen3.8-flash-next spent all 40,000 output tokens on reasoning (`reasoning_tokens: 40000`, `finish_reason=length`) and wrote no answer. At temperature 0 every re-run did the same, so the PR could never get a review, and "split the PR" could not help.

Now an answer cut off before any of its text is put back once under the answer schema (oMLX bounds the reasoning near 4,096 tokens there), asking for the whole review again, with the end of the earlier reasoning quoted as unfinished notes. A second cut-off fails the check with both errors in the comment. An answer cut off after it started writing still fails closed at once with the cap status, so a finding it had already written cannot be lost.

The new tests reject: a reasoning-only cut-off going straight to the error status instead of a retry, the retry asking under no schema or without the quoted reasoning, a mid-answer cut-off being retried, and a double cut-off passing. Four of them fail on the old script.

## forgejo-actions, 2026-11-22T17:29:23-08:00

<!-- ai-review -->
**AI review** of `b7078135f7`: The PR correctly addresses issue #121 by distinguishing reasoning-only cut-offs from mid-answer cut-offs, retrying the former under the answer schema while keeping the latter failing closed. The implementation is sound, tests cover the key scenarios, and the diff is appropriately scoped.

No findings.
(The model's first answer was rejected (no JSON object in the model's answer); this is its second, with any finding the first had that it left out.)


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
