# #72 Adopt the rules in SisyphusMD/dreame-valetudo

- Kind: issue, state: closed, by cody, created 2026-11-17T07:54:22-08:00
- Labels: status:in-progress, type:chore; milestone: none

Found auditing every SisyphusMD repo on 2026-11-17: dreame-valetudo has none of the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), no nightly issue-archive and no .forgejo/RULES.md, so its required checks are its own CI only. Bring it in per docs/adopting.md (An existing repo): workflows, scripts, issue templates and labels, RULES.md copy, CONTRIBUTING.md, protection with the rules' checks proven on a PR first, annex mirror and issue-archive.

## cody, 2026-11-17T13:32:28-08:00

State 2026-11-17 (handing over to a Codex session): adoption not started in substance. A clean worktree exists at ~/repos/SisyphusMD/.worktrees/dreame-valetudo-adopt on branch ci/adopt-project-rules from verified main 86b5de1 (after dreame #293), no changes, nothing pushed. Plan follows appliance-job-monitor (#73, done in its PRs #8-#10): copy the gate workflows, scripts, templates, RULES.md, SECURITY.md and mirror-lockdown.yml verbatim; rename the repo's own ci.yml to tests.yml (name: Tests); exempt the copied pull_request_target jobs in test_trust_gates_also_exclude_agit_pull_requests (_UNGATED_ON_PULL_REQUESTS); exclude .forgejo/scripts and vendored packaging from ruff (#85); Renovate leaves the copies alone; CONTRIBUTING gets the rule 9 line, SECURITY pointer and exact required-check names; then GitHub Actions on for the copy, limited to the lockdown action.

## cody, 2026-11-17T13:34:28-08:00

Resuming adoption in the existing ci/adopt-project-rules worktree. Branch protection waits for the required check proofs and the release change in #86.

## cody, 2026-11-17T14:45:27-08:00

Dreame adoption PR dreame-valetudo#296 merged at 001e66b and both mirrors match. Its issue archive ran successfully. The existing Tests workflow keeps its CI display name to preserve live required contexts. GitHub mirror lockdown is dreame-valetudo#299. Stricter protection remains open pending release conversion and check proof.

## cody, 2026-11-17T14:57:05-08:00

Dreame #299 merged at 9ad3964. GitHub and annex match the exact Forgejo tip. GitHub Actions has only the SHA-pinned lockdown workflow active. Existing main protection is in place while #86 release conversion and gate proof continue.

## cody, 2026-11-17T23:57:38-08:00

Dreame adoption is complete. Adoption, release promotion and generated Tap publisher landed in dreame-valetudo#296, dreame-valetudo#301 and dreame-valetudo#303. Required-check proof is in dreame-valetudo#304. Approved v0.3.0-rc.52 passed the release and installation paths. Verified strict main protection on 47b1bc891097e70cc6e7d55ca9d3e87b2a20ea85 with 13 required contexts. Direct pushes are disabled for all users, including admins. PRs must be up to date. Both main mirrors match.

https://forgejo.bryantserver.com/SisyphusMD/dreame-valetudo/actions/runs/1835
