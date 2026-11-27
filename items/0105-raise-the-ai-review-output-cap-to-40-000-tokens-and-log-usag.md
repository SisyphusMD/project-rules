# #105 Raise the AI review output cap to 40,000 tokens and log usage

- Kind: pull, state: closed, by cody, created 2026-11-19T09:58:52-08:00
- Labels: none; milestone: none
- refs/pull/105/head -> main, merged: True

Closes #104
Closes #103

The review's model output cap was 16,000 tokens. The model's hidden reasoning counts toward it, so long reviews were cut off before the JSON verdict and failed closed (a private repo twice; a private repo #63 three times, each 3m37s, which is about 16,000 tokens at the observed speed).

- One fixed cap of 40,000, overridable per repo with `MAX_OUTPUT_TOKENS`. Sizing: a replay of a private repo's prompt needed 23,557 output tokens (23,119 reasoning) and finished in 308 s; the context window is 262,144, and at the slowest seen speed (59 tok/s) 40,000 tokens fit inside the 900 s request timeout.
- A cut-off answer (`finish_reason=length`) fails closed before parsing, with a status that says to split the PR instead of re-running.
- Every run logs the model's token usage, so the cap can be re-checked against real reviews.
- New tests cover the cap sent, the usage log, a cut-off answer, an empty answer and the override.

The copies in other repos follow once this merges.

## forgejo-actions, 2026-11-19T10:14:11-08:00

<!-- ai-review -->
**AI review** of `7814a84820`: The PR correctly raises the output cap to 40,000 tokens, adds a CutOff exception with fail-closed handling, logs usage, and ships thorough tests for ask_model. One coverage gap remains on the new except-CutOff branch in main().

### Open

- **F1** (suggestion, `.forgejo/scripts/ai-review.py:281`) CutOff handler in main() may lack branch coverage: CONTRIBUTING.md requires 100% branch coverage on .forgejo/scripts/. The new `except CutOff` block in main() (lines 281-284) is a new branch. The new test file exercises ask_model directly but does not call main() with a mocked ask_model that raises CutOff. If no pre-existing test already drives main() through this path, coverage will fall below 100%. Consider adding a small test that patches ask_model to raise CutOff and asserts set_status is called with the expected message and sys.exit is reached.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICIuZm9yZ2Vqby9zY3JpcHRzL2FpLXJldmlldy5weSIsICJsaW5lIjogMjgxLCAic2V2ZXJpdHkiOiAic3VnZ2VzdGlvbiIsICJzdGF0dXMiOiAib3BlbiIsICJ0aXRsZSI6ICJDdXRPZmYgaGFuZGxlciBpbiBtYWluKCkgbWF5IGxhY2sgYnJhbmNoIGNvdmVyYWdlIiwgImRldGFpbCI6ICJDT05UUklCVVRJTkcubWQgcmVxdWlyZXMgMTAwJSBicmFuY2ggY292ZXJhZ2Ugb24gLmZvcmdlam8vc2NyaXB0cy8uIFRoZSBuZXcgYGV4Y2VwdCBDdXRPZmZgIGJsb2NrIGluIG1haW4oKSAobGluZXMgMjgxLTI4NCkgaXMgYSBuZXcgYnJhbmNoLiBUaGUgbmV3IHRlc3QgZmlsZSBleGVyY2lzZXMgYXNrX21vZGVsIGRpcmVjdGx5IGJ1dCBkb2VzIG5vdCBjYWxsIG1haW4oKSB3aXRoIGEgbW9ja2VkIGFza19tb2RlbCB0aGF0IHJhaXNlcyBDdXRPZmYuIElmIG5vIHByZS1leGlzdGluZyB0ZXN0IGFscmVhZHkgZHJpdmVzIG1haW4oKSB0aHJvdWdoIHRoaXMgcGF0aCwgY292ZXJhZ2Ugd2lsbCBmYWxsIGJlbG93IDEwMCUuIENvbnNpZGVyIGFkZGluZyBhIHNtYWxsIHRlc3QgdGhhdCBwYXRjaGVzIGFza19tb2RlbCB0byByYWlzZSBDdXRPZmYgYW5kIGFzc2VydHMgc2V0X3N0YXR1cyBpcyBjYWxsZWQgd2l0aCB0aGUgZXhwZWN0ZWQgbWVzc2FnZSBhbmQgc3lzLmV4aXQgaXMgcmVhY2hlZC4iLCAicmVzcG9uc2UiOiAiIn1d -->

## cody, 2026-11-19T11:05:23-08:00

Added a main() test for the cut-off status (F1). Retrying the review: the last run returned an unparseable answer after 45 s.

## cody, 2026-11-19T11:13:08-08:00

The two failed reviews on 926715e were not the cap: the Studio's reasoning parser ended the reasoning at a literal </think> the model quoted from this diff (the re.sub line), so the rest of its reasoning leaked into the answer ahead of the verdict and the old brace regex could not parse it. 70ca224 parses the whole answer first, then what follows each </think>, and each attempt must parse as one object to the end. A replay of the failed review's real reply now parses.

Declined from cross-model review: rejecting an unfinished verdict that quotes </think> and happens to end in a nested verdict-shaped object. By accident that is vanishingly unlikely, and output steered on purpose could already be a clean verdict, so stricter parsing adds no protection.

## cody, 2026-11-19T11:14:42-08:00

Retrying the review: the last run hit a transient URLError; the model endpoint answers normally now.

## cody, 2026-11-19T13:39:58-08:00

Picking this up from cody-36 (the earlier session has been quiet since 11:14). Retrying the review.

## cody, 2026-11-19T13:40:15-08:00

Correction from cody-36: this PR was already merged at 12:17; my earlier pickup note was based on a stale status. Nothing to do here.
