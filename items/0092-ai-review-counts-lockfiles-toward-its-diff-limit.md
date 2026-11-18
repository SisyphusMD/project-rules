# #92 AI review counts lockfiles toward its diff limit

- Kind: issue, state: open, by cody, created 2026-11-17T13:17:11-08:00
- Labels: status:ready, type:bug; milestone: none

`diff-size.py` leaves lockfiles out (its `LOCKFILES` set), but `ai-review.py` sends the whole diff and fails any PR over `MAX_DIFF_CHARS` (120000) with "split the PR". A PR that adds a `uv.lock` (~94k characters) fails the AI review although Diff size passes it (bryantserver/casa#62, where the lockfile had to land in its own PR).

Fix: drop lockfile hunks from the diff the AI review sends, using the same set as `diff-size.py` (shared, not a second copy that can drift), and tell the model they were omitted. Test: a diff whose only oversize part is a lockfile is reviewed, not refused.
