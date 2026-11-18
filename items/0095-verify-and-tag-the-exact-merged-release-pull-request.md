# #95 Verify and tag the exact merged release pull request

- Kind: pull, state: closed, by cody, created 2026-11-17T14:04:51-08:00
- Labels: none; milestone: none
- refs/pull/95/head -> main, merged: True

Closes #96
Refs #86

Add the shared verifier and tag-only publisher for the two-step release flow. The verifier rejects a PR that has not merged into this repository's main, a different candidate tree, and a tag that conflicts with the primary's published tags. The existing release helper invocation still works while repositories migrate.

Tests use a real local Git remote to prove an exact release can be tagged after main advances, a retry preserves the existing tag object, and a conflicting tag leaves both refs intact. The shared Python suite passed with 90 tests and one existing skip. The existing mirror tests and ShellCheck passed.

The repository workflows and live release proof follow under #86. Keep that issue open until a protected-branch release has passed.

## forgejo-actions, 2026-11-17T14:10:46-08:00

<!-- ai-review -->
**AI review** of `59c33d0e0c`: The PR adds a well-structured verifier and tag-only publisher for the two-step release flow, with comprehensive tests using a real local Git remote. The logic for merge-commit verification, tree matching, changelog validation, tag conflict detection, and the push-tag.sh --merged-commit path are all correct and well-tested. One suggestion about the Forgejo API label format assumption.

### Open

- **F1** (suggestion, `shared/packaging/verify-release-pr.py:30`) head["label"] format may include owner prefix in real Forgejo API: The code does `branch = head["label"]` then `tag = branch.removeprefix("release/")`. The test fixture uses `"label": "release/v1.2.3"`, but in Gitea/Forgejo's PR API, `head.label` for a same-repo PR is typically `owner:branch` (e.g. `Owner:release/v1.2.3`). If the real API returns the owner-prefixed form, `removeprefix("release/")` would not strip anything, `VERSION.fullmatch` would return None, and every legitimate release PR would be rejected with "expected a release/vX.Y.Z head branch". The test passes because it constructs the dict manually. Verify against the actual Forgejo instance's API response (e.g. `curl .../repos/Owner/Project/pulls/7 | jq .head.label`) and either adjust the parsing (e.g. `branch.rsplit(":", 1)[-1]` or a regex that tolerates the prefix) or confirm the label truly is bare for same-repo PRs in the version deployed.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJzaGFyZWQvcGFja2FnaW5nL3ZlcmlmeS1yZWxlYXNlLXByLnB5IiwgImxpbmUiOiAzMCwgInNldmVyaXR5IjogInN1Z2dlc3Rpb24iLCAic3RhdHVzIjogIm9wZW4iLCAidGl0bGUiOiAiaGVhZFtcImxhYmVsXCJdIGZvcm1hdCBtYXkgaW5jbHVkZSBvd25lciBwcmVmaXggaW4gcmVhbCBGb3JnZWpvIEFQSSIsICJkZXRhaWwiOiAiVGhlIGNvZGUgZG9lcyBgYnJhbmNoID0gaGVhZFtcImxhYmVsXCJdYCB0aGVuIGB0YWcgPSBicmFuY2gucmVtb3ZlcHJlZml4KFwicmVsZWFzZS9cIilgLiBUaGUgdGVzdCBmaXh0dXJlIHVzZXMgYFwibGFiZWxcIjogXCJyZWxlYXNlL3YxLjIuM1wiYCwgYnV0IGluIEdpdGVhL0Zvcmdlam8ncyBQUiBBUEksIGBoZWFkLmxhYmVsYCBmb3IgYSBzYW1lLXJlcG8gUFIgaXMgdHlwaWNhbGx5IGBvd25lcjpicmFuY2hgIChlLmcuIGBPd25lcjpyZWxlYXNlL3YxLjIuM2ApLiBJZiB0aGUgcmVhbCBBUEkgcmV0dXJucyB0aGUgb3duZXItcHJlZml4ZWQgZm9ybSwgYHJlbW92ZXByZWZpeChcInJlbGVhc2UvXCIpYCB3b3VsZCBub3Qgc3RyaXAgYW55dGhpbmcsIGBWRVJTSU9OLmZ1bGxtYXRjaGAgd291bGQgcmV0dXJuIE5vbmUsIGFuZCBldmVyeSBsZWdpdGltYXRlIHJlbGVhc2UgUFIgd291bGQgYmUgcmVqZWN0ZWQgd2l0aCBcImV4cGVjdGVkIGEgcmVsZWFzZS92WC5ZLlogaGVhZCBicmFuY2hcIi4gVGhlIHRlc3QgcGFzc2VzIGJlY2F1c2UgaXQgY29uc3RydWN0cyB0aGUgZGljdCBtYW51YWxseS4gVmVyaWZ5IGFnYWluc3QgdGhlIGFjdHVhbCBGb3JnZWpvIGluc3RhbmNlJ3MgQVBJIHJlc3BvbnNlIChlLmcuIGBjdXJsIC4uLi9yZXBvcy9Pd25lci9Qcm9qZWN0L3B1bGxzLzcgfCBqcSAuaGVhZC5sYWJlbGApIGFuZCBlaXRoZXIgYWRqdXN0IHRoZSBwYXJzaW5nIChlLmcuIGBicmFuY2gucnNwbGl0KFwiOlwiLCAxKVstMV1gIG9yIGEgcmVnZXggdGhhdCB0b2xlcmF0ZXMgdGhlIHByZWZpeCkgb3IgY29uZmlybSB0aGUgbGFiZWwgdHJ1bHkgaXMgYmFyZSBmb3Igc2FtZS1yZXBvIFBScyBpbiB0aGUgdmVyc2lvbiBkZXBsb3llZC4iLCAicmVzcG9uc2UiOiAiIn1d -->

## cody, 2026-11-17T14:12:01-08:00

F1 checked against the primary Forgejo API. Same-repo merged PRs GhostSpectator #24, Archiver #348 and Dreame #293 return a bare branch in head.label. After deletion head.ref becomes refs/pull/<number>/head, while head.label and head.sha retain the original values. The verifier and deleted-branch test use that observed contract.
