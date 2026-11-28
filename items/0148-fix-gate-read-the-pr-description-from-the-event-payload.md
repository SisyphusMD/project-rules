# #148 fix(gate): read the PR description from the event payload

- Kind: pull, state: closed, by cody, created 2026-11-27T08:23:57-08:00
- Labels: none; milestone: none
- refs/pull/148/head -> main, merged: True

Closes #147

The gate scripts read the PR description from the event payload at `GITHUB_EVENT_PATH` instead of a `PR_BODY` environment variable, which Linux refuses past 128 KB (`exec /usr/bin/bash: argument list too long`). `PR_BODY` still overrides, for the tests. A missing payload or a non-PR event now exits with a message saying so, rather than looking like an empty description.

Proof run, reverted before merge (the branch's tree equals the fix commit): a temporary workflow called from Tests ran this branch's `issue-link.py` with no `PR_BODY`, while this description was padded to 138,853 bytes. It read the whole body from the event payload inside the called workflow and passed. The gate jobs on that head, which run main's scripts, failed with `argument list too long`, the bug this fixes.

Found on the way: Forgejo re-evaluates a caller job's `if:` inside the called workflow, where `github.event_name` is not `pull_request`, so an `event_name == 'pull_request'` clause on a `uses:` job skips it.


## forgejo-actions, 2026-11-27T08:29:29-08:00

<!-- ai-review -->
**AI review** of `924d9fd3c1`: Clean fix for #147: the three gate scripts now read the PR body from the event payload file instead of the environment, with PR_BODY kept as a test override. The new test file covers all branches of pr_body() (large body, empty/None, missing path, non-PR event, override) and guards the workflow against reintroducing free-text env vars. No issues found.

### Resolved

- **F1** (suggestion, `.forgejo/workflows/ci.yml:20`) Verify temporary branch references are reverted before merge: The diff as presented contains no @issue-147-pr-body-file or --branch issue-147-pr-body-file references; the PR states the temporary commit is removed before merge. The submitted diff is clean.
  - Reviewer: The diff no longer contains the temporary branch references, so this is resolved for the code as submitted. The proof-147.yml workflow and its tests.yml caller are clearly labelled temporary and will be dropped before merge.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICIuZm9yZ2Vqby93b3JrZmxvd3MvY2kueW1sIiwgImxpbmUiOiAyMCwgInNldmVyaXR5IjogInN1Z2dlc3Rpb24iLCAic3RhdHVzIjogInJlc29sdmVkIiwgInRpdGxlIjogIlZlcmlmeSB0ZW1wb3JhcnkgYnJhbmNoIHJlZmVyZW5jZXMgYXJlIHJldmVydGVkIGJlZm9yZSBtZXJnZSIsICJkZXRhaWwiOiAiVGhlIGRpZmYgYXMgcHJlc2VudGVkIGNvbnRhaW5zIG5vIEBpc3N1ZS0xNDctcHItYm9keS1maWxlIG9yIC0tYnJhbmNoIGlzc3VlLTE0Ny1wci1ib2R5LWZpbGUgcmVmZXJlbmNlczsgdGhlIFBSIHN0YXRlcyB0aGUgdGVtcG9yYXJ5IGNvbW1pdCBpcyByZW1vdmVkIGJlZm9yZSBtZXJnZS4gVGhlIHN1Ym1pdHRlZCBkaWZmIGlzIGNsZWFuLiIsICJyZXNwb25zZSI6ICJUaGUgZGlmZiBubyBsb25nZXIgY29udGFpbnMgdGhlIHRlbXBvcmFyeSBicmFuY2ggcmVmZXJlbmNlcywgc28gdGhpcyBpcyByZXNvbHZlZCBmb3IgdGhlIGNvZGUgYXMgc3VibWl0dGVkLiBUaGUgcHJvb2YtMTQ3LnltbCB3b3JrZmxvdyBhbmQgaXRzIHRlc3RzLnltbCBjYWxsZXIgYXJlIGNsZWFybHkgbGFiZWxsZWQgdGVtcG9yYXJ5IGFuZCB3aWxsIGJlIGRyb3BwZWQgYmVmb3JlIG1lcmdlLiJ9XQ== -->
