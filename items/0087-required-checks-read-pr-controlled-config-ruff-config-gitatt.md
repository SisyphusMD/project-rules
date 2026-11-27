# #87 Required checks read PR-controlled config (ruff config, .gitattributes)

- Kind: issue, state: open, by cody, created 2026-11-17T11:12:31-08:00
- Labels: status:ready, type:bug; milestone: none

Two `ci.yml` gates run on the PR checkout with settings the PR itself can change, so a PR can weaken the check that judges it (rule 17: gates run from the base):

- **Lint**: `ruff check .` loads `ruff.toml`/`pyproject.toml` and their exclusions from the PR checkout. The workflow should supply trusted settings and file scope from the base commit.
- **Secrets**: gitleaks scans git patch output from the PR checkout. A PR-controlled `.gitattributes` that marks paths binary suppresses their text hunks. The scan should not honor PR-controlled diff attributes (for example, `-c core.attributesFile=/dev/null` and an empty info/attributes, or scanning with `--text`).

Found by review while adopting appliance-job-monitor (#73). Related: #85 (consumer ruff defaults).

## cody, 2026-11-17T11:17:53-08:00

Also from review of the #70 copy: the Secrets job fails open if a gitleaks bump changes `--log-opts` handling (it exits 0 when it scans nothing). Guard with `git cat-file -e "$HEAD_SHA^{commit}"` before the scan and a positive control (a throwaway repo with a fake secret must exit 1). Pass the SHAs through `env:` like the other jobs, and drop `fetch-depth: 0` for the fetch-on-demand pattern the other jobs use.
