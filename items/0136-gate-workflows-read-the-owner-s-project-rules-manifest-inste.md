# #136 Gate workflows read the owner's .project-rules manifest instead of house hosts

- Kind: issue, state: open, by cody, created 2026-11-26T09:18:33-08:00
- Labels: status:needs-decision, type:feature; milestone: none

Step 1 of the build order in #133, part 2 of 3. gate-lint (package index, release mirror), review.yml (llm_url, ai_review exemption) and issue-archive (bot email) read `${server_url}/${owner}/.project-rules` env.json, cloned from its main before any PR checkout, and fail closed when it is missing or invalid. An exempt owner's `AI review` passes naming the cited issue. No instance hostnames left in .forgejo/ (a test holds it). The RULES.md scope line, rule 15 and rule 21 move to the manifest wording in the same PR, since they describe this behaviour.

Depends on #134.

## cody, 2026-11-26T10:00:15-08:00

Status: PR #140 is open and held, not merged. Proven on the real runner in #140's Tests run: the read step cloned SisyphusMD/.project-rules with the job token and logged `owner manifest: SisyphusMD/.project-rules 415be50a`, then the drift step got HTTP 403 on bryantserver/.project-rules.

Blocker: the bryantserver org's visibility is private, so its repos' job tokens cannot read bryantserver/.project-rules (probed 2026-11-26: 403 with the token, and anonymous fails too). In a limited-visibility org the job token can read it (probed on a throwaway org, since deleted). Merging now would fail Lint, Secrets and AI review in every bryantserver repo. This needs Cody's call: switch the bryantserver org to limited visibility (its private repos stay private), or another way for bryantserver repos to read their manifest.

Next once that is settled: merge #140, then a real consumer PR showing Lint, Secrets and AI review green on the manifest.

## cody, 2026-11-26T10:33:14-08:00

Status: #140 proven before merge, still held.

- A throwaway private repo, cody/manifest-gate-probe (since deleted), called gate.yml, gate-lint.yml and review.yml at `@feat/136-read-manifest`. Its PR got Issue link, Tests with code, Diff size, Lint, Secrets and AI review all green; Lint, Secrets and Review each logged `owner manifest: cody/.project-rules c59b07d5`, and gitleaks found no leaks.
- issue-archive.yml dispatched from the branch in project-rules (run 48442) read SisyphusMD/.project-rules and pushed the archive with the same committer address as before.
- #140's Tests job now also checks each value the reader validated arrives unchanged in later steps; on the runner it logged the house PACKAGE_INDEX and BOT_EMAIL. Its drift step still gets 403 on bryantserver/.project-rules.
- Probed visibility: a public manifest in a limited-visibility org is readable with a job token from the same org and from another owner (cody), and unreadable anonymously; in a private org it is unreadable both ways. So limited would make every bryantserver job and this drift check work.
- Follow-up in #140: `manifest.py` accepted no dot-leading repo in an exemption, so `owner/.project-rules#n` was refused; now accepted (`.` and `..` still refused). CONTRIBUTING names five Tests checks.

Before merging: Cody's call on bryantserver's visibility; protect main on the three manifest repos (org members renovate, and anna in bryantserver, may have push through teams); after merge, add `Tests / The owner manifests can be read and agree (pull_request)` to this repo's required checks, then run a consumer proof per owner.
