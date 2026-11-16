# #21 Open Forgejo to outside contributors; GitHub copies mirror-only

- Kind: issue, state: open, by cody, created 2026-11-16T14:07:28-08:00
- Labels: status:needs-decision, type:feature; milestone: none

_Recreated from bryantserver/project-rules#21 (issue, opened by cody on 2026-11-16)._

Decision on #1 (Cody, 2026-11-16). To work out before anything is opened:
- Sign-up: who can register, spam and abuse limits (the Anubis gate already fronts Forgejo).
- Fork PRs: the gates run on pull_request_target and never run PR code; confirm they check out a fork's head and that secrets stay out of anything the PR controls.
- Cost: AI review and runner time spent on strangers' PRs (limit per user, or first-time contributors need a maintainer's go).
- GitHub: disable issues and PRs on each public repo's GitHub copy and point its README to Forgejo. Outward-facing; each repo needs Cody's OK.
- Public CONTRIBUTING.md in each public repo pointing to the public rules.
