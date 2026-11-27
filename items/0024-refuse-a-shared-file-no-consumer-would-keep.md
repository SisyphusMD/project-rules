# #24 Refuse a shared file no consumer would keep

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:29-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#3 (pull request, opened by cody on 2026-08-23, merged 2026-08-23). Branch `refs/pull/3/head` into `main`._

Consumers enumerate Renovate `fileFilters`. A shared file outside that shape is written on the update branch, dropped before the commit, and leaves a lock describing content the branch does not have.

Only this end can refuse the first such file: the consumers can check what is already in their lock, not what a future tag will add.
