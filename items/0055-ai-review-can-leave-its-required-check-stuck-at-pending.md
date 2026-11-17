# #55 AI review can leave its required check stuck at pending

- Kind: issue, state: open, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:ready, type:bug; milestone: none

From a house-model review on 2026-11-16, confirmed on main: the status goes to pending first and only paths inside the try clear it. The job has timeout-minutes: 20 but ask_model may wait 900 s plus API calls, so a slow model gets the job killed with the check left pending; binascii.Error from a trimmed state marker is not caught; and the final set_status calls are unguarded. A pending required check blocks every merge until break-glass. Fix: job timeout above the script's worst case, catch everything at the top to set error, guard the terminal set_status. Tests for each path.
