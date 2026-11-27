# #144 issue-archive runs from project-rules main like the gate

- Kind: issue, state: open, by cody, created 2026-11-27T06:38:26-08:00
- Labels: status:in-progress, type:feature; milestone: none

Every repo copies issue-archive.yml and .forgejo/scripts/issue-archive.py, and the copies fall behind whenever main changes them: after #140 every consumer's two files differ from main. Make the job a reusable workflow here (called from main, script fetched from main like the gate scripts), so each repo keeps only a small caller with the schedule, concurrency and the PROJECT_RULES_TOKEN mapping, and drops its script copy. The job still pushes the calling repo's own issue-archive branch with that repo's job token. Prove it from a branch before merge, then roll out one PR per repo. Decided on #141 (Cody, 2026-11-27).
