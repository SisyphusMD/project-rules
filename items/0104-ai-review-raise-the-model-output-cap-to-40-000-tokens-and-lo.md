# #104 AI review: raise the model output cap to 40,000 tokens and log usage

- Kind: issue, state: closed, by cody, created 2026-11-19T09:55:26-08:00
- Labels: status:in-progress, type:bug; milestone: none

The review asks the model for at most 16,000 output tokens. The model reasons before answering and its hidden reasoning counts against that cap, so long reviews end with finish_reason=length and no JSON verdict; the required check then fails closed with nothing wrong in the PR.

Evidence: bryantserver/k8s PR 2572 failed twice this way (16,000 tokens generated on 9,355- and 9,443-token prompts). Replaying its prompt with no effective cap finished in 308 s at 77 tok/s using 23,557 output tokens (23,119 reasoning), with a valid verdict.

Plan (Cody approved 2026-11-19): one fixed cap of 40,000, no retry. Context is 262k so it is not the limit; the 900 s request timeout is. At the slowest seen speed (59 tok/s) 40,000 tokens take about 11 minutes, under 15. Also print the model's usage on every run so the cap can be re-checked against real reviews. Then carry the change to every repo that copies the script.

## cody, 2026-11-19T12:17:10-08:00

Decision: Admin-merge #105 past its failing AI review check ("Yes"). Why: The review runs main's script, which has the </think> parse bug #105 fixes, and #105's own diff contains that tag, so its review cannot pass until it merges.

Decided by: Cody, 2026-11-19.
