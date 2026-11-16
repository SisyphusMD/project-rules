# #33 fix(release): compare the mirrored tag object, since a reused tag name answers 200 while stale

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:32-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#13 (pull request, opened by cody on 2026-08-29, merged 2026-08-29). Branch `refs/pull/13/head` into `main`._

The confirmation added in v0.1.22 checked only that GitHub answered 200 for the tag name. An rc number is derived from the source tags alone, so a name can be reused, and a ref left behind by a partial prune answers 200 while still pointing at the previous release - every job waiting on the mirror would then run against the wrong commit.

Compares the object the mirror serves with the one just pushed. The test gains that case.
