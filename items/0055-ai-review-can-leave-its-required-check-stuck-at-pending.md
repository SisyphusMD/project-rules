# #55 AI review can leave its required check stuck at pending

- Kind: issue, state: closed, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:in-progress, type:bug; milestone: none

From a house-model review on 2026-11-16, confirmed on main: the status goes to pending first and only paths inside the try clear it. The job has timeout-minutes: 20 but ask_model may wait 900 s plus API calls, so a slow model gets the job killed with the check left pending; binascii.Error from a trimmed state marker is not caught; and the final set_status calls are unguarded. A pending required check blocks every merge until break-glass. Fix: job timeout above the script's worst case, catch everything at the top to set error, guard the terminal set_status. Tests for each path.

## cody, 2026-11-19T17:00:34-08:00

Now hitting live with the 40,000-token cap (#105). casa #81's review step started 00:38:45Z and the job was killed at the 20-minute limit at 00:58:44Z (job 199020), with no usage line logged and the check left pending. cody/macos #63's review is on the same path (started 00:44Z). The 900 s urlopen timeout never fired, so it limits each socket read rather than the whole call; something on the path must be sending bytes before the answer is done. Generating up to 40,000 tokens can take longer than the job allows, so this blocks reviews of large diffs in every repo that copies the script. Fix needed: a total deadline in ask_model below the job limit that sets an error status, plus a job timeout above the script's worst case. — cody-36 (owner of the review-script sync)

## cody, 2026-11-19T17:20:00-08:00

Decision: Raise the AI review job limit from 20 to 45 minutes, with a 40-minute total deadline on the model call (Cody: "Yes"). Why: Reviews at the 40,000-token cap outlast 20 minutes and get killed with the check stuck pending (casa #81, macos #63).

Decided by: Cody, 2026-11-19.

## cody, 2026-11-19T17:35:22-08:00

Technical call: The 40-minute deadline covers the whole review from the script's start through the comment write, not the model call alone. Why: A deadline on the model call alone leaves the reads before it and the comment write unbounded, which is how the job got killed with the check pending; normal setup takes seconds, so the model keeps nearly all 40 minutes.

Decided by: Claude, 2026-11-19.

## cody, 2026-11-19T17:35:22-08:00

Left out of the fix: the terminal status write after the alarm is off still has only api()'s 60 s per-read timeout. A Forgejo response that trickles without committing could in principle outlast the 5-minute margin. Not seen in practice; bound it separately if it ever shows up.

## cody, 2026-11-19T17:36:57-08:00

More data: casa #81's rerun passed in 9m41s and casa #85 in 7m22s, once the 11 concurrent sync reviews had cleared. The 20-minute kills came from queueing on the shared Studio, not from generation time alone. The deadline in #108 still matters, because a busy Studio is exactly when reviews queue.
