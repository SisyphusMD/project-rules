# #144 issue-archive runs from project-rules main like the gate

- Kind: issue, state: closed, by cody, created 2026-11-27T06:38:26-08:00
- Labels: status:in-progress, type:feature; milestone: none

Every repo copies issue-archive.yml and .forgejo/scripts/issue-archive.py, and the copies fall behind whenever main changes them: after #140 every consumer's two files differ from main. Make the job a reusable workflow here (called from main, script fetched from main like the gate scripts), so each repo keeps only a small caller with the schedule, concurrency and the PROJECT_RULES_TOKEN mapping, and drops its script copy. The job still pushes the calling repo's own issue-archive branch with that repo's job token. Prove it from a branch before merge, then roll out one PR per repo. Decided on #141 (Cody, 2026-11-27).

## cody, 2026-11-27T07:14:02-08:00

Merged in #145 (main a7a3b3e) and proven in a consumer: a dispatched Issue archive run in a repo using the new caller pushed its archive as the owner bot. Rollout PRs are open in the other 13 repos.

## cody, 2026-11-27T08:25:49-08:00

Rollout done: all 14 house repos now call archive.yml and no longer carry the script (one issue and PR in each, merged and verified on main; branches removed). No repo copies issue-archive.py any more.
