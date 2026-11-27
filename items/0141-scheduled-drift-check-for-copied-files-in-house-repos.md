# #141 Scheduled drift check for copied files in house repos

- Kind: issue, state: open, by cody, created 2026-11-26T09:55:19-08:00
- Labels: status:needs-decision, type:feature; milestone: none

Follow-up to #78, agreed there: a scheduled job here compares each house repo's copied files with this repo's main and reports a difference.

## What it compares
The files docs/adopting.md has repos copy: `.forgejo/workflows/ci.yml`, `ai-review.yml`, `issue-archive.yml`, `.forgejo/scripts/issue-archive.py`, the issue templates, and `.github/workflows/mirror-lockdown.yml` for a public repo.

## Baseline, 2026-11-26 (by hand, credential-store token)
14 repos call the shared gate. 10 are byte-equal on every file. Left:
- a private repo: bug, decision and feature templates reworded for a private repo (front matter `about` and the prose prompts).
- a private repo: no issue templates at all (a missing house standard; its own issue and PR there).
- several private repos: ci.yml and ai-review.yml are the allowed variant (own Lint and Secrets, no ISSUE_READ_TOKEN mapping).

## Plan
- Discovery, no names in this repo: every repo the token can read whose owner keeps a `.project-rules` manifest and whose ci.yml calls this repo's gate.yml. Host from `github.server_url`.
- Callers are compared as parsed YAML against adopting.md's rule rather than bytes: same `name`, triggers and concurrency; every shared call present and equal, except a repo may drop the ISSUE_READ_TOKEN mapping and may drop `shared-lint` when it has its own `Lint` and `Secrets` jobs; other extra jobs are allowed. issue-archive.yml, issue-archive.py and mirror-lockdown.yml are byte-compared.
- Issue templates: compared on front matter `name`, `title` and `labels` only, since a repo may reword the prompts for its own users (a private repo does).
- Reporting: one issue here, opened when drift appears, commented only when the set of differences changes, closed when it clears. No red run per day (notification policy).
- Read access: the job token cannot read other owners' private repos and ISSUE_READ_TOKEN is read:issue only, so it needs a new secret. Scope pending Cody's decision.
- Tests with fixture repos for each case; workflow_dispatch so the branch run proves it before merge.

Depends on nothing; runs alongside #136 (if #136 changes issue-archive.yml, repos drift until they update, which is what this check is for).

## cody, 2026-11-26T10:16:27-08:00

Technical call: The Copy drift read token (secret COPY_DRIFT_READ_TOKEN) is read:repository limited to the private repos the check reads (several private repos; several private repos); public repos need no token. A private repo that adopts the rules is added by re-minting the token (docs/adopting.md). Why: The other 27 private repos on the host do not copy these files, so the check never reads them; an account-wide token would expose them all for nothing (Cody, 2026-11-26: "Those other 35 private repos don't need it?").

Decided by: Claude, 2026-11-26.
