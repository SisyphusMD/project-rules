# #71 Adopt the rules in SisyphusMD/whiskerless

- Kind: issue, state: closed, by cody, created 2026-11-17T07:54:21-08:00
- Labels: status:in-progress, type:chore; milestone: none

Found auditing every SisyphusMD repo on 2026-11-17: whiskerless has none of the rules' gate workflows (issue link, tests with code, diff size, lint, secrets, AI review), no nightly issue-archive and no .forgejo/RULES.md, so its required checks are its own CI only. Bring it in per docs/adopting.md (An existing repo): workflows, scripts, issue templates and labels, RULES.md copy, CONTRIBUTING.md, protection with the rules' checks proven on a PR first, annex mirror and issue-archive.

## cody, 2026-11-17T13:40:33-08:00

Starting adoption from verified main 32f4b8af after #210. The existing CI display name will be kept while moving its workflow to tests.yml to preserve the five existing job families and their protected contexts.

## cody, 2026-11-17T14:45:27-08:00

Whiskerless adoption PR whiskerless#213 merged at 9b0221d and both mirrors match. Its issue archive ran successfully. The existing Tests workflow keeps its CI display name to preserve live required contexts. GitHub mirror lockdown is whiskerless#216. Stricter protection remains open pending release conversion and check proof.

## cody, 2026-11-17T15:02:28-08:00

Whiskerless #216 merged at be0c1b3. GitHub and annex match the exact Forgejo tip. GitHub Actions has only the SHA-pinned lockdown workflow active. Existing main protection is in place while #86 release conversion and gate proof continue.

## cody, 2026-11-17T23:57:37-08:00

Whiskerless adoption is complete. Adoption, release promotion and generated Tap publisher landed in whiskerless#213, whiskerless#223 and whiskerless#227. Required-check proof is in whiskerless#225. Approved v0.2.0-rc.78 passed the release and installation paths. Verified strict main protection on 903e4d20c622907b490f952ca0035782cac540b6 with 15 required contexts. Direct pushes are disabled for all users, including admins. PRs must be up to date. Both main mirrors match.

https://forgejo.bryantserver.com/SisyphusMD/whiskerless/actions/runs/1417
