# #73 Adopt the rules in SisyphusMD/appliance-job-monitor

- Kind: issue, state: closed, by cody, created 2026-11-17T07:54:22-08:00
- Labels: status:ready, type:chore; milestone: none

Found auditing every SisyphusMD repo on 2026-11-17: appliance-job-monitor has none of the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), no nightly issue-archive and no .forgejo/RULES.md, so its required checks are its own CI only. Bring it in per docs/adopting.md (An existing repo): workflows, scripts, issue templates and labels, RULES.md copy, CONTRIBUTING.md, protection with the rules' checks proven on a PR first, annex mirror and issue-archive.

## cody, 2026-11-17T16:32:30-08:00

Appliance adoption is complete. SisyphusMD/appliance-job-monitor#5 records the positive and negative gate proofs, verified main protection and the live v0.1.1 release.
