# #60 No Renovate config, so nothing here is ever updated

- Kind: issue, state: closed, by cody, created 2026-11-17T06:50:12-08:00
- Labels: status:ready, type:bug; milestone: none

The cluster Renovate runs with requireConfig=required, so a repo without its own config is skipped. This repo has none: the pinned action SHAs in .forgejo/workflows, the ruff and pytest pins in tests.yml and the shellcheck image in shared/packaging/shellcheck-all.sh never get update PRs, and consumers inherit stale pins on every re-vendor. project-standard had a config covering exactly these; port it.
