# #76 Adopt the rules in SisyphusMD/homebrew-tap

- Kind: issue, state: closed, by cody, created 2026-11-17T07:54:23-08:00
- Labels: status:in-progress, type:chore; milestone: none

Found auditing every SisyphusMD repo on 2026-11-17: homebrew-tap has none of the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), no nightly issue-archive and no .forgejo/RULES.md, so its required checks are its own CI only. Bring it in per docs/adopting.md (An existing repo): workflows, scripts, issue templates and labels, RULES.md copy, CONTRIBUTING.md, protection with the rules' checks proven on a PR first, backup mirror and issue-archive.

## cody, 2026-11-17T13:38:03-08:00

The tap has no branch protection. Dreame and Whiskerless publish formula and bottle updates by pushing to its main branch. Adoption can add rules and checks, but enabling protection also depends on moving those automated tap updates to pull requests.

## cody, 2026-11-17T13:45:10-08:00

Starting tap adoption. Forgejo issues and pull requests are currently disabled on this repository, so enable both on the primary to run issue-first adoption. Keep direct publisher pushes available until the publisher workflows can use pull requests.

## cody, 2026-11-17T14:19:47-08:00

Tap #2 settled at cd7a3f8. The Ruby syntax check passed, both mirrors match and the issue archive ran and synced to a private repo. Strict main protection waits for homebrew-tap #3. GitHub lockdown follows verification of the mirror credential.

## cody, 2026-11-17T14:45:27-08:00

Homebrew Tap #5 merged at 65aa04b after the scoped GitHub mirror credential rotation. Both mirrors match and GitHub Actions has only the SHA-pinned lockdown workflow active. Strict main protection remains open pending homebrew-tap#3 and check proof.

## cody, 2026-11-17T23:57:38-08:00

Homebrew Tap adoption is complete. Homebrew-tap#3 and homebrew-tap#9 record the negative proof and positive provenance proof from both live release publishers. Verified strict main protection on e5b884b9779569f0919cae017e6d835a791bf042 with 8 required contexts. Direct pushes are disabled for all users, including admins. PRs must be up to date. Both main mirrors match.
