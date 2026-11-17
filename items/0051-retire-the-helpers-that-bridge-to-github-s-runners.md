# #51 Retire the helpers that bridge to GitHub's runners

- Kind: issue, state: closed, by cody, created 2026-11-16T18:01:55-08:00
- Labels: none; milestone: none

Cody has decided (2026-11-16) that no SisyphusMD job will run on GitHub-hosted runners. The macOS CI, the release builds and the install matrix all move to our own runners, and the GitHub mirrors stop running Actions.

Several shared helpers exist only to bridge to GitHub's runners, and they become dead weight once the product repos stop using them:
- `check-mirror-ci.sh`: waits for GitHub's ci-macos and formula-macos verdict on a SHA.
- `triage-infra-failure.py`: classifies failures for GitHub's retry-infra-failures workflow.
- `forgejo-preflight.sh`: lets GitHub-hosted runners probe for a CrowdSec ban on Forgejo.
- the GitHub half of `check-rc-install-matrix.sh`.

`macos-scope.sh` also has a gap: it treats every `.forgejo/` path as Linux-only. A Renovate branch that changes only `.forgejo/workflows/macos.yml` therefore skips the Mac run that would test that very change.

Wanted:
- a Forgejo-side gate that waits for a workflow's run on a SHA, replacing `check-mirror-ci.sh`;
- `check-rc-install-matrix.sh` reading the single Forgejo `install-matrix.yml` run for the candidate;
- the GitHub-only helpers and their tests retired;
- `macos-scope.sh` running the Mac whenever `macos.yml` changes;
- docs and VARIANCE updated to match.
