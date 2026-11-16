# #8 Lint uses main's config, not the PR's

- Kind: issue, state: open, by cody, created 2026-11-16T14:07:22-08:00
- Labels: status:ready, type:bug; milestone: none

_Recreated from bryantserver/project-rules#8 (issue, opened by cody on 2026-11-16)._

a second-model review review of the CI move: Lint runs ruff and yamllint in the PR checkout, so a PR can add a ruff.toml (lint.ignore = ["ALL"]) or .yamllint and pass its own lint. Rule 15 says a PR cannot weaken the check that judges it. Fix: restore linter config from the base commit before linting, as Secrets does for gitleaks allowlists. Same gap in bryantserver/casa's copy.
