# #19 AI review reads the rules, CONTRIBUTING.md and the linked issue

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:27-08:00
- Labels: type:feature; milestone: none

_Recreated from bryantserver/project-rules#19 (issue, opened by cody on 2026-11-16, closed 2026-11-16)._

Part of #2. The reviewer reads only README.md, which here (and in every repo after adoption) no longer holds the rules, and it never sees the linked issue, so it cannot judge rule 7 (every hunk maps to the issue). Give it RULES.md (vendored as .forgejo/RULES.md in other repos, kept in sync by #3), CONTRIBUTING.md, README.md for what the project is, and each linked issue with its recent comments. Scope creep and an unsound `No tests:` or `Large diff:` reason become blocking.

## cody, 2026-11-16T14:07:27-08:00

_cody, 2026-11-16 12:01:_

Technical call: The AI review blocks on scope creep (a hunk that neither serves the linked issue nor is needed for it) and on a No tests: or Large diff: reason that does not hold. Why: Cody decided the craft rules carry over with CI and the AI review as the gate (#1); a suggestion-only finding would leave rules 7 and 8 unenforced.

Decided by: agent, 2026-11-16.
