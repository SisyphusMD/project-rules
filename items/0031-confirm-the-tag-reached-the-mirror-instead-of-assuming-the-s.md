# #31 Confirm the tag reached the mirror instead of assuming the sync worked

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:31-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#11 (pull request, opened by cody on 2026-08-29, merged 2026-08-29). Branch `refs/pull/11/head` into `main`._

dreame rc.41 failed its publish at "tag never appeared on GitHub": the push-mirror had errored with context deadline exceeded and Forgejo does not retry, so the job waiting for the tag timed out ten minutes later, far from the cause.

push_mirrors-sync answers 403 to the repo-scoped token the release uses, which is why the call has always been best-effort — so a retry keyed on its result would never run. What is checkable without extra scope is the OUTCOME: the GitHub mirror is public, so an unauthenticated ref lookup says whether the tag arrived.

One bounded POST, then read-only polling, three-state: arrived / definitively absent / unknown. A check that cannot answer reports unknown rather than claiming failure. Still warn-only — a release whose refs already fanned out must not be failed by a mirror.

Also: ci.yml named one test file explicitly, so tests/*.sh added later never ran. It now discovers them.
