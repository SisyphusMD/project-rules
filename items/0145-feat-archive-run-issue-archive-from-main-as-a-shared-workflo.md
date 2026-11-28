# #145 feat(archive): run issue-archive from main as a shared workflow

- Kind: pull, state: closed, by cody, created 2026-11-27T06:53:57-08:00
- Labels: none; milestone: none
- refs/pull/145/head -> main, merged: True

issue-archive becomes a shared workflow like the gate. `archive.yml` here holds the job, and it runs `.forgejo/scripts/issue-archive.py` fetched from main. Each repo's `issue-archive.yml` shrinks to a caller: the schedule, the concurrency group and the `PROJECT_RULES_TOKEN` mapping. Repos no longer copy the script.

Why: after #140 every consumer's copies of both files differ from main. A copy only gets updated when someone remembers to re-copy it.

- Tests: the archive job must use only the fetched script; its fetch and manifest-read steps match the proven ones; the caller maps only the manifest token; `tests.yml` now also compiles issue-archive.py, since a broken main copy would now break every repo's archive.
- docs/adopting.md: the caller is copied and the script is not; a repo that still has the script deletes it.
- The job is now named `Archive`, so its status context reads `Issue archive / Archive`. Nothing requires it.

Proof: run 487, dispatched from this branch with the caller temporarily pointing at the branch (that commit is reverted here). The called job fetched main's scripts, read SisyphusMD/.project-rules, and pushed this repo's issue-archive branch as the manifest's bot address.

Rollout after merge: one PR per repo that swaps in the new caller and deletes the script copy.

Closes #144


## forgejo-actions, 2026-11-27T06:54:59-08:00

<!-- ai-review -->
**AI review** of `8264c2b249`: The PR correctly converts issue-archive into a shared workflow called from main, with the canonical caller now referencing @main (resolving F1). Tests, docs, and the changelog are updated consistently. No new issues found.

### Resolved

- **F1** (blocking, `.forgejo/workflows/issue-archive.yml:16`) Canonical caller references the feature branch, not main: The `uses` line now reads `SisyphusMD/project-rules/.forgejo/workflows/archive.yml@main`, matching the PR description's claim that the branch reference was reverted. The test `test_the_canonical_callers_call_main_and_hand_over_only_the_two_read_tokens` will pass.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICIuZm9yZ2Vqby93b3JrZmxvd3MvaXNzdWUtYXJjaGl2ZS55bWwiLCAibGluZSI6IDE2LCAic2V2ZXJpdHkiOiAiYmxvY2tpbmciLCAic3RhdHVzIjogInJlc29sdmVkIiwgInRpdGxlIjogIkNhbm9uaWNhbCBjYWxsZXIgcmVmZXJlbmNlcyB0aGUgZmVhdHVyZSBicmFuY2gsIG5vdCBtYWluIiwgImRldGFpbCI6ICJUaGUgYHVzZXNgIGxpbmUgbm93IHJlYWRzIGBTaXN5cGh1c01EL3Byb2plY3QtcnVsZXMvLmZvcmdlam8vd29ya2Zsb3dzL2FyY2hpdmUueW1sQG1haW5gLCBtYXRjaGluZyB0aGUgUFIgZGVzY3JpcHRpb24ncyBjbGFpbSB0aGF0IHRoZSBicmFuY2ggcmVmZXJlbmNlIHdhcyByZXZlcnRlZC4gVGhlIHRlc3QgYHRlc3RfdGhlX2Nhbm9uaWNhbF9jYWxsZXJzX2NhbGxfbWFpbl9hbmRfaGFuZF9vdmVyX29ubHlfdGhlX3R3b19yZWFkX3Rva2Vuc2Agd2lsbCBwYXNzLiIsICJyZXNwb25zZSI6ICIifV0= -->
