# #62 Decide where security reports go

- Kind: issue, state: closed, by cody, created 2026-11-17T06:50:13-08:00
- Labels: status:in-progress, type:decision; milestone: none

conventions/code.md section 7 requires security and support routing. No SisyphusMD repo has it: Forgejo has no private advisories or confidential issues, and no repo publishes a contact address. Needs a maintainer decision on the private channel (for example a dedicated address) before a SECURITY.md can exist here and in each consumer.

## cody, 2026-11-17T09:02:28-08:00

Decision: Security reports go to security@bryantserver.com, a Fastmail alias delivering to the maintainer (filed to Tech/Security Reports). Every repo gets a SECURITY.md pointing there, and the CONTRIBUTING template and adoption guide ask for it. Why: Every project already lives on bryantserver.com, so the address reveals nothing new; a dedicated alias can be filtered or retired without exposing a personal address, and Forgejo has no private advisories.

Decided by: Cody, 2026-11-17.

## cody, 2026-11-17T09:22:32-08:00

Technical call: the alias is security@bryantserver.com, filed to its own Fastmail folder; the MX for bryantserver.com is Fastmail. An end-to-end test message from outside is still owed before this is called proven.

Technical call: `SECURITY.md` is copied once at adoption, like CONTRIBUTING.md. Nothing in a consumer checks it stays identical; `docs/adopting.md` and the adoption issues #71 to #76 are the enforcement, and each adoption PR re-copies `.forgejo/RULES.md` with it. This repo's own pair is kept identical by `tests/test_security_policy.py`.

Technical call: "only the latest release is supported" holds for every SisyphusMD repo today; a repo that ever supports two release lines edits its copy.

Technical call: a security fix's issue lives in a private repo until the fix is released (the rule 23 route), recorded as a row in the RULES.md Exceptions table.

## cody, 2026-11-17T11:01:45-08:00

Verified 2026-11-17: a test message from an outside Gmail account to security@bryantserver.com arrived in Fastmail in the Security Reports folder.
