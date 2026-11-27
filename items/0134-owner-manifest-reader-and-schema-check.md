# #134 Owner manifest reader and schema check

- Kind: issue, state: closed, by cody, created 2026-11-26T09:18:05-08:00
- Labels: status:in-progress, type:feature; milestone: none

Step 1 of the build order in #133, part 1 of 3. A gate script that validates an owner's `<owner>/.project-rules/env.json` (mirror_url, llm_url, ai_review, package_index, release_mirror, bot_email), turns it into job env lines, and checks drift between owners on the keys meant to match. Nothing calls it yet; the workflow switch is the next issue. Manifest repos can run the same script on their own env.json.

## cody, 2026-11-26T10:00:14-08:00

Status: merged in #138 (merge cd9f60a2). `.forgejo/scripts/manifest.py` validates, exports and drift-checks owner manifests; 100% branch coverage, Tests and all gate checks green. The three house manifests pass `check` and `drift`. Nothing calls it until #136 merges. Next: #136.
