# #38 feat(packaging): macos-scope.sh — let Renovate branches skip the GitHub macOS workflows when only Linux-side files change

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:33-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#29 (pull request, opened by cody on 2026-10-26, merged 2026-10-26). Branch `refs/pull/29/head` into `main`._

Every push to main makes Renovate rebase its whole backlog, and each rebased branch queued two macOS runs on the GitHub mirror (~30 per main push), most for Dockerfile digests or Forgejo workflows no Mac reads. Real verdicts waited hours behind them.

`macos-scope.sh <ref>` prints true/false. Only `refs/heads/renovate/*` can be skipped, and only when every changed path (renames split with --no-renames) is on an anchored Linux-only list. Anything undecidable runs.

Consumers gate their ci-macos.yml / formula-macos.yml jobs on it next, and let renovate/* runs cancel superseded ones.
