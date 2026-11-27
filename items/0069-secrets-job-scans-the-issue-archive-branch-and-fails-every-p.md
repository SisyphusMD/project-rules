# #69 Secrets job scans the issue-archive branch and fails every PR on issue text

- Kind: issue, state: closed, by cody, created 2026-11-17T07:41:55-08:00
- Labels: status:in-progress, type:bug; milestone: none

Found 2026-11-17 on a private repo PR #53, the first PR after adopting the rules: CI / Secrets failed with 2 generic-api-key hits, both alembic revision IDs quoted in an old issue body, which the nightly issue-archive commit copied into items/*.md and json/items.json.

Cause: the Secrets job checks out with fetch-depth 0, so the clone holds origin/issue-archive, and `gitleaks git` scans every ref. Issue text is not code; and because issue-archive is re-committed every night, .gitleaksignore fingerprints (which carry the commit SHA) for it go stale, so there is no durable allowlist fix.

Fix: scan only the history the PR head carries (`--log-opts=<head sha>`). Verified locally: the same clone scans clean with --log-opts=HEAD; the full-ref scan reports the 2 archive hits.

Claude (session repos-79) has this.

## cody, 2026-11-17T07:51:10-08:00

Technical call: The Secrets job scans only the PR head history; issue-archive is not scanned anywhere. Why: A secret pasted into an issue is already exposed on the forge, and the archive copy adds no exposure a scan could prevent; archive commits change SHA nightly, so no allowlist can hold. Rule 15 names the check, not its scope.

Decided by: Claude, 2026-11-17.
