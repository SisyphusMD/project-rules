# #2 Move the playbook, skill template and shared CI into this repo

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:20-08:00
- Labels: type:chore; milestone: none

_Recreated from bryantserver/project-rules#2 (issue, opened by cody on 2026-11-16, closed 2026-11-16)._

Canonical home for docs/playbooks/issue-driven-projects.md and skills/project-issues/template/.forgejo (CI, AI review, issue archive), now in cody/agents. The skill stays in cody/agents as a thin pointer. Add the upstream craft rules (see the decision on #1), a Diff size check with a `Large diff: <reason>` hatch, and have the AI reviewer read these rules plus the repo's CONTRIBUTING.md and the linked issue instead of the README. Also: issue-link must accept cross-repo refs (owner/repo#n), and the playbook's 'revise after Casa phase 1' stays.

## cody, 2026-11-16T14:07:20-08:00

_cody, 2026-11-16 07:23:_

Rules text landed on main as d34843d (RULES.md, docs/new-project.md, templates/CONTRIBUTING.md); annex mirror confirmed at the same commit. Next: move the CI and AI-review workflows here as-is, then separate PRs for the Diff size check, cross-repo issue links, and the AI reviewer reading RULES.md, CONTRIBUTING.md and the linked issue.

## cody, 2026-11-16T14:07:20-08:00

_cody, 2026-11-16 07:34:_

Status 2026-11-16: CI, AI review and issue-archive moved here (#10, merged 45b82e7; Issue link failed only at bootstrap because main had no scripts). Bootstrap trigger dropped (#11, 28ba85d), the first run of every gate from main, all green, AI review no findings. main is now protected like Casa (no direct push, admins included, up to date, 0 approvals; Issue link, Tests with code, Lint, Secrets, AI review). Issue archive dispatched once: issue-archive branch fefd68a, on annex too. Remaining on this issue, each its own PR: Diff size check, cross-repo issue links, the reviewer reading RULES.md + CONTRIBUTING.md + the linked issue, and cody/agents' skill template becoming a pointer here. Related: #8 lint config from main, #9 script tests.

## cody, 2026-11-16T14:07:21-08:00

_cody, 2026-11-16 11:54:_

Technical call: Cross-repo issue links are checked with ISSUE_READ_TOKEN, an Actions secret on the bryantserver org and the cody user holding a read:issue-only token under cody (Forgejo name project-rules-issue-read). Verified: reads casa and cody/macos issues, write refused (403). Not stored elsewhere; re-mint with the admin CLI to rotate. Why: A probe showed the built-in Actions token gets 404 on any other private repo; Cody approved minting a token over a format-only check (2026-11-16).

Decided by: agent, 2026-11-16.

## cody, 2026-11-16T14:07:21-08:00

_cody, 2026-11-16 12:05:_

Done. Moved and extended here: CI/AI review/archive (#10, #11), Diff size (#15, required on main after a pass in #18 and a deliberate fail in #16), owner/repo#n links (#18), reviewer reads RULES.md + CONTRIBUTING.md + linked issues and blocks scope creep (#20). cody/agents f8164fa: the project-issues skill points here; its template and the old playbook are deleted. Follow-ups: #3 apply-to-every-repo script (also syncs .forgejo/ and .forgejo/RULES.md), #7 Casa onto these copies, #8 lint config from main, #9 tests for the remaining scripts.
