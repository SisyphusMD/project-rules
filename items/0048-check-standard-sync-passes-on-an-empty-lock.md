# #48 check-standard-sync passes on an empty lock

- Kind: issue, state: open, by cody, created 2026-11-16T14:17:55-08:00
- Labels: status:ready, type:bug; milestone: none

Found in the second-model review of the first commit. shared/packaging/check-standard-sync.py reports in sync when STANDARD.lock lists no files, so a consumer whose lock was emptied (by mistake or by a PR) passes the drift check with nothing checked. Fix: an empty or missing file list fails, with a test.
