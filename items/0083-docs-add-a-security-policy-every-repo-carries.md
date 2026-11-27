# #83 docs: add a security policy every repo carries

- Kind: pull, state: closed, by cody, created 2026-11-17T09:23:15-08:00
- Labels: none; milestone: none
- refs/pull/83/head -> main, merged: True

Closes #62

A vulnerability had no private channel: issues and pull requests are public. `SECURITY.md` now says to email security@bryantserver.com (a Fastmail alias filed to its own folder), what to include, that only the latest release is supported, and that disclosure is coordinated with the reporter. `templates/SECURITY.md` is the identical copy every repo carries.

- Rule 22 now requires a `SECURITY.md` alongside `CONTRIBUTING.md`, and `docs/adopting.md` adds it to both the new-repo and existing-repo steps (existing repos get it through #71 to #76).
- The Exceptions table records the route for a security fix: its issue lives in a private repo (rule 23) until the fix is released, and the PR describes the change, not the exploit.
- `tests/test_security_policy.py` rejects the two copies differing; with a line appended to the template it fails with "SECURITY.md and templates/SECURITY.md differ".

The judgment calls are recorded on #62. Delivery is proven: a test message from an outside Gmail account arrived in the Security Reports folder.


Main was merged in after #84 landed; the only conflict was the changelog, resolved by keeping both entries.


## forgejo-actions, 2026-11-17T09:23:29-08:00

<!-- ai-review -->
**AI review** of `748dc1c05a`: Clean, well-scoped PR that adds a security policy, its template, a drift test, and the corresponding rule/doc updates. Every hunk serves issue #62, the diff is small, and the test correctly guards the two copies against divergence.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->

## cody, 2026-11-17T11:05:06-08:00

Retrying the AI review: the last run failed to reach the model (URLError). The new commit only merges main in; the diff against main is unchanged.
