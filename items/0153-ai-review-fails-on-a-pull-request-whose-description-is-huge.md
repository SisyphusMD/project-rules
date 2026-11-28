# #153 AI review fails on a pull request whose description is huge

- Kind: issue, state: closed, by cody, created 2026-11-27T19:16:48-08:00
- Labels: status:in-progress, type:bug; milestone: none

A Renovate group PR whose description carried about 1 MB of release notes failed AI review in about a second: "Review could not run: HTTPError", logged as "review failed closed: HTTP Error 400: Bad Request". The prompt includes the whole PR description unbounded, while the diff, replies and linked issues are each bounded, so the request passes the model's context. Fix: clip the description like a reply (keep its start and end, where Renovate puts the issue reference) to a fixed bound; keep reading issue references from the whole description.

## cody, 2026-11-27T19:23:54-08:00

Done in #154 (merged at 2e986757): the description is clipped to 20,000 characters and the linked issues to 40,000, references still come from the whole description, and a refused model request shows its HTTP code and message in the check. No copied file changed. Proof pending: the re-run review on the 1 MB Renovate PR that hit this.
