# #136 Gate workflows read the owner's .project-rules manifest instead of house hosts

- Kind: issue, state: closed, by cody, created 2026-11-26T09:18:33-08:00
- Labels: type:feature; milestone: none

Step 1 of the build order in #133, part 2 of 3. gate-lint (package index, release mirror), review.yml (llm_url, ai_review exemption) and issue-archive (bot email) read `${server_url}/${owner}/.project-rules` env.json, cloned from its main before any PR checkout, and fail closed when it is missing or invalid. An exempt owner's `AI review` passes naming the cited issue. No instance hostnames left in .forgejo/ (a test holds it). The RULES.md scope line, rule 15 and rule 21 move to the manifest wording in the same PR, since they describe this behaviour.

Depends on #134.

## cody, 2026-11-26T10:00:15-08:00

Status: PR #140 is open and held, not merged. Proven on the real runner in #140's Tests run: the read step cloned SisyphusMD/.project-rules with the job token and logged `owner manifest: SisyphusMD/.project-rules 415be50a`, then the drift step got HTTP 403 on bryantserver/.project-rules.

Blocker: the bryantserver org's visibility is private, so its repos' job tokens cannot read bryantserver/.project-rules (probed 2026-11-26: 403 with the token, and anonymous fails too). In a limited-visibility org the job token can read it (probed on a throwaway org, since deleted). Merging now would fail Lint, Secrets and AI review in every bryantserver repo. This needs Cody's call: switch the bryantserver org to limited visibility (its private repos stay private), or another way for bryantserver repos to read their manifest.

Next once that is settled: merge #140, then a real consumer PR showing Lint, Secrets and AI review green on the manifest.

## cody, 2026-11-26T10:33:14-08:00

Status: #140 proven before merge, still held.

- A throwaway private repo (since deleted) called gate.yml, gate-lint.yml and review.yml at `@feat/136-read-manifest`. Its PR got Issue link, Tests with code, Diff size, Lint, Secrets and AI review all green; Lint, Secrets and Review each logged `owner manifest: cody/.project-rules c59b07d5`, and gitleaks found no leaks.
- issue-archive.yml dispatched from the branch in project-rules (run 48442) read SisyphusMD/.project-rules and pushed the archive with the same committer address as before.
- #140's Tests job now also checks each value the reader validated arrives unchanged in later steps. Its drift step still gets 403 on bryantserver/.project-rules.
- Probed visibility: a public manifest in a limited-visibility org is readable with a job token from the same org and from another owner (cody), and unreadable anonymously; in a private org it is unreadable both ways. So limited would make every bryantserver job and this drift check work.
- Follow-up in #140: `manifest.py` accepted no dot-leading repo in an exemption, so `owner/.project-rules#n` was refused; now accepted (`.` and `..` still refused). CONTRIBUTING names five Tests checks.

Before merging: Cody's call on bryantserver's visibility; protect main on the three manifest repos (org members renovate, and anna in bryantserver, may have push through teams); after merge, add `Tests / The owner manifests can be read and agree (pull_request)` to this repo's required checks, then run a consumer proof per owner.

## cody, 2026-11-26T20:35:53-08:00

Status: #140 reworked for the private-manifest decision and the owner keys, history rewritten to one commit, still held.

- The read step now clones with the owner's `PROJECT_RULES_TOKEN` (fails before trying when it is unset), and its errors name neither the git host's address nor any value. The canonical callers map that secret in; probed that an unmapped owner secret reaches a called job empty.
- Schema: owner keys `visibility`, `mirrors`, `decided_by`, `bot_email`; host keys `llm_url`, `ai_review`, `package_index`, `release_mirror`. Drift compares host keys only. All four house manifests carry it, and humblepixels/.project-rules now exists (private, labels and docs as the others).
- The drift and handoff checks moved to a new `Owners` workflow with the nightly visibility check. It runs on `pull_request_target`, push, schedule and dispatch, never the PR's code, since its token reads every owner's manifest. The manifest repo itself must be private under either policy.
- Review findings rejected: a private repo under a public owner stays out of the bot's sight (it gets no wider access by decision); exemption citations stay in statuses, since a public owner cites its own public repo.

Blocked: the reader bot does not exist yet (creating a user needs site admin, and the admin route was refused here), and every caller must map the secret before #140 merges (#143).


## cody, 2026-11-26T22:36:20-08:00

Status: merged in #140 (main 5ac366d). Every consumer maps `PROJECT_RULES_TOKEN` (#143), a proof PR per owner read its own manifest in Lint, Secrets and Review, and the two Owners checks are required on main. Details on #143.
