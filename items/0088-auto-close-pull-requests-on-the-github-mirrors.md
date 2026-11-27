# #88 Auto-close pull requests on the GitHub mirrors

- Kind: issue, state: closed, by cody, created 2026-11-17T11:51:06-08:00
- Labels: status:in-progress, type:feature; milestone: none

GitHub cannot turn pull requests off, so the read-only GitHub copies still accept them. Cody's decision (2026-11-17): do what most read-only mirrors do, a GitHub Action (`dessant/repo-lockdown`) that closes and locks any new PR with a comment pointing to Forgejo.

Plan:
- `.github/workflows/mirror-lockdown.yml` in project-rules, pinned by SHA, guarded with `if: github.server_url == 'https://github.com'` so it never runs on Forgejo (a repo without `.forgejo/workflows/` would otherwise run it there), `permissions: {}` at the top and `pull-requests: write` on the job, no checkout.
- `docs/adopting.md` tells every repo to copy it; each repo gets it with its adoption (#71 to #76), appliance-job-monitor in its own PR.
- On each GitHub copy: Actions on, limited to this one action, default token read-only.

## cody, 2026-11-17T12:13:15-08:00

Verified 2026-11-17 on the project-rules GitHub copy: a test PR (GitHub #1) was closed and locked within seconds by github-actions[bot] with the Forgejo pointer comment; the run succeeded on pull_request_target. Actions there: enabled, selected actions only (this one, SHA-pinned), SHA pinning required, read-only default token. Test branch deleted.
