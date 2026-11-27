# #139 docs(rules): add the preview-branch rule and say git host

- Kind: pull, state: closed, by cody, created 2026-11-26T09:28:28-08:00
- Labels: none; milestone: none
- refs/pull/139/head -> main, merged: True

Closes #137

Trigger: the client-site repos take changes on `staging` for a preview and only promote an approved commit to `main` (fit check on #133), which rules 6 and 19 did not allow for. Cody's 2026-11-26 decision on #133 makes it a generic rule.

- Rule 6: a repo may name a preview branch in its `CONTRIBUTING.md`. Changes, Renovate's included, land there through pull requests the same way, and `main` takes only promotion pull requests pinning a commit that passed the preview checks and was approved.
- Rule 19: the preview branch is protected like `main`, so direct pushes to it stop.
- Rule 15: the checks run the workflow from the protected branch the PR targets, which for a preview PR is the preview branch (Forgejo reads `pull_request_target` workflows from the target).
- Rule 20: git host, not forge.
- `docs/adopting.md`: protect the preview branch too and add it to `ci.yml`'s branches; the template gets a `Preview branch` section.

Folded into existing rules so no rule is renumbered: rules 21 to 23 are cited across every repo. Rule 21's wording changes with the manifest switch (#136), not here. No code changes.

## forgejo-actions, 2026-11-26T09:28:58-08:00

<!-- ai-review -->
**AI review** of `b0ce24f705`: Clean, well-scoped docs-only PR that adds the preview-branch rule to rules 6, 15, and 19, changes 'forge' to 'git host' in rule 20, and updates the adopting guide and CONTRIBUTING template accordingly. All changes map to issue #137. One trivially unrelated blank-line removal in the changelog.

### Open

- **F1** (suggestion, `CHANGELOG.md:10`) Unrelated blank-line removal in changelog: The diff deletes a blank line between the `manifest.py` entry and the 'caller headers' entry. This is unrelated to the preview-branch rule (#137). Rule 8 says 'no unrelated cleanup.' It's one line so not blocking, but it would be cleaner to leave it or fold it into a separate formatting PR.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJDSEFOR0VMT0cubWQiLCAibGluZSI6IDEwLCAic2V2ZXJpdHkiOiAic3VnZ2VzdGlvbiIsICJzdGF0dXMiOiAib3BlbiIsICJ0aXRsZSI6ICJVbnJlbGF0ZWQgYmxhbmstbGluZSByZW1vdmFsIGluIGNoYW5nZWxvZyIsICJkZXRhaWwiOiAiVGhlIGRpZmYgZGVsZXRlcyBhIGJsYW5rIGxpbmUgYmV0d2VlbiB0aGUgYG1hbmlmZXN0LnB5YCBlbnRyeSBhbmQgdGhlICdjYWxsZXIgaGVhZGVycycgZW50cnkuIFRoaXMgaXMgdW5yZWxhdGVkIHRvIHRoZSBwcmV2aWV3LWJyYW5jaCBydWxlICgjMTM3KS4gUnVsZSA4IHNheXMgJ25vIHVucmVsYXRlZCBjbGVhbnVwLicgSXQncyBvbmUgbGluZSBzbyBub3QgYmxvY2tpbmcsIGJ1dCBpdCB3b3VsZCBiZSBjbGVhbmVyIHRvIGxlYXZlIGl0IG9yIGZvbGQgaXQgaW50byBhIHNlcGFyYXRlIGZvcm1hdHRpbmcgUFIuIiwgInJlc3BvbnNlIjogIiJ9XQ== -->
