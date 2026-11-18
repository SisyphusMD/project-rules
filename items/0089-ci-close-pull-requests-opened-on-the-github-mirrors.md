# #89 ci: close pull requests opened on the GitHub mirrors

- Kind: pull, state: closed, by cody, created 2026-11-17T11:54:13-08:00
- Labels: none; milestone: none
- refs/pull/89/head -> main, merged: True

Closes #88

GitHub cannot turn pull requests off, so the read-only GitHub copies still accept them. `.github/workflows/mirror-lockdown.yml` closes and locks a new one with a comment pointing to the Forgejo repo and its GitHub sign-in, as most read-only mirrors do, using `dessant/repo-lockdown` v5.0.2 pinned by commit.

What keeps it safe, each pinned by `tests/test_mirror_lockdown.py`:
- It runs only on GitHub under the SisyphusMD owner: Forgejo runs `.github/workflows` in a repo without `.forgejo/workflows`, where it would close the real pull requests, and a fork with Actions on would close its own. Commenting the condition out or dropping the owner check fails the test.
- The token is `permissions: {}` with only `pull-requests: write` on the job; an extra permission fails the test.
- No checkout and no `run:` step, so nothing from the pull request executes.
- The daily sweep skips pull requests created before 2026-11-17, so the closed history (already answered and moved to Forgejo) is not commented on or locked. Removing the cut-off fails the test.

Rule 21 and `docs/adopting.md` (step 1) say every public repo copies it and its GitHub copy has Actions on, limited to this action, with a read-only default token. Each repo gets it with its adoption (#71 to #76).

## forgejo-actions, 2026-11-17T11:54:54-08:00

<!-- ai-review -->
**AI review** of `474dbd779f`: Clean, well-scoped PR that adds a pinned, minimally-permissioned GitHub Actions workflow to auto-close PRs on read-only GitHub mirrors, with a solid test file pinning every safety property, and matching docs/changelog updates. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
