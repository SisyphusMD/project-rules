# #149 Compile copies-match.py in the gate-fetch test once it is on main

- Kind: issue, state: closed, by cody, created 2026-11-27T08:29:50-08:00
- Labels: status:in-progress, type:chore; milestone: none

The Tests job "The gate scripts can be fetched" compiles every gate script fetched from main. copies-match.py (#146) cannot join that list until it is on main, since the job reads main, not the PR. After #146 merges, add copies-match to the list in .forgejo/workflows/tests.yml, so a broken main copy of the script fails a Tests check before it fails the Copies match check in every repo.

Depends on #141.

## cody, 2026-11-27T09:49:13-08:00

Done in #150 (main e019857).
