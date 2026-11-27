# #119 fix(ai-review): the re-ask can pass a lost review and drops the first answer's findings

- Kind: issue, state: closed, by cody, created 2026-11-21T18:33:43-08:00
- Labels: status:ready, type:bug; milestone: none

A qx review of canonical `.forgejo/scripts/ai-review.py` at 0e929cc (run on the SisyphusMD/homebrew-tap copy, #113) found these in the re-ask added by #110/#114. I checked each against the code; they hold.

1. **Fail-open on a retry.** Before the re-ask, an unreadable answer always ended in `error`. Now, on a first review (no prior state), a first answer that raises NoJSON or "no choices", followed by a schema-valid `{"summary": ..., "findings": []}`, sets `success`. The strict schema allows an empty findings array, and a model confused by the rejection, or one cut short by oMLX's ~4096-token reasoning cap, can return exactly that. Nothing tells "found nothing" apart from "lost the review". Options: a retried run with no findings ends `failure` with a note to re-run, or the retry must restate every id that the first answer's lenient parse yielded.
2. **A successful retry drops the first answer's good findings.** `fallback` (the first answer's well-formed findings plus prior) is used only when the second answer also fails. When the retry succeeds, a finding present only in the first answer vanishes from the comment and the saved state. Merge `fallback` into the result by id, the same carry-over rule `validate` applies to prior findings.
3. **A CutOff on the retry names the wrong cap.** The retry is capped at RESTATE_OUTPUT_TOKENS (16000), but `main`'s message quotes MAX_OUTPUT_TOKENS and advises raising it.
4. **The carry-over check re-checks `line` but not `file`.** A saved blocker whose file left the diff still blocks, while the same finding from the model is downgraded.
5. **Check live:** that `ref: ${{ github.sha }}` checks out main on `pull_request_target`. homebrew-tap#24 is the first such run; its checkout log names the commit. If Forgejo gives a merge or head commit there, use `github.event.pull_request.base.sha || github.sha`.

Lower: the retry ends with two user turns and no assistant turn; `clip()` returns up to limit+7 characters; the workflow comment "a test holds them equal" is true only in project-rules, not in the copies.

Copies (#113) go ahead as canonical; this fix gets copied after it lands.

## cody, 2026-11-21T18:44:32-08:00

Technical call: A clean retry after an unreadable first answer still passes, labelled 'after a retry' in the status; a carried blocker whose file left the diff keeps blocking (qx item 4 rejected). Why: Failing every retried run would fail clean PRs whose first answer was malformed, and the retry quotes the first answer and its reasoning; downgrading a saved blocker would fail open.

Decided by: Claude, 2026-11-21.
