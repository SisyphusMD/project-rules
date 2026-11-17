# #53 feat(shared): gate releases on Forgejo's macOS run and retire the GitHub-runner helpers

- Kind: pull, state: closed, by cody, created 2026-11-16T18:15:39-08:00
- Labels: none; milestone: none
- refs/pull/53/head -> main, merged: True

Closes #51

Large diff: most of it is deletion. Three retired helpers and their tests go (about 1,200 lines). What's added is a replacement gate and two stub-driven test scripts.

**Trigger:** Cody decided on 2026-11-16 that no SisyphusMD job runs on GitHub-hosted runners. These shared helpers existed only to bridge to those runners:
- `check-mirror-ci.sh` waited for GitHub's ci-macos/formula-macos verdict;
- `triage-infra-failure.py` drove GitHub's retry-infra-failures workflow;
- `forgejo-preflight.sh` was the CrowdSec edge-ban probe for GitHub-hosted runners;
- `check-rc-install-matrix.sh` read the GitHub half of the install matrix.

**What changes:**
- **`check-forgejo-ci.sh <sha> <workflow-file>`** (new) waits for that workflow's run on that exact commit on Forgejo.
  - A run counts only if it concluded `success` AND every job in it succeeded. A run whose macOS jobs were scoped out (a Renovate branch) also concludes `success` and tested nothing. cx review reproduced that against whiskerless 7c8605f, and the gate now refuses it; checked live, it rejects 7c8605f and accepts whiskerless main e595096.
  - A 401/403 fails at once. 5xx and curl failures are retried until the timeout.
  - The SHA and workflow name are validated before they go into a URL.
  - `FORGEJO_CI_TOKEN` is optional, since the repos are public.
- **`check-rc-install-matrix.sh`** is Forgejo only.
  - Every workflow in `INSTALL_MATRIX_WORKFLOWS` must be green for the newest candidate (default `install-matrix.yml`; a blank list is refused).
  - The newest-candidate check asks Forgejo's tag refs instead of GitHub's (a 404 there means there are none).
  - Re-dispatch recognition by job name is unchanged.
  - Checked live: dreame v0.3.0-rc.50 passes with both of its matrix workflows.
- **`macos-scope.sh`:** a Renovate branch that touches `.forgejo/workflows/macos.yml` now runs the Mac. Before, all of `.forgejo/` counted as Linux-only, so a bump to the macOS workflow skipped the run that tests it. The GitHub workflow entries are gone from the skip list.
- **`tools/capability-diff.py`:** drops the GitHub-only probes (ci-pr, infra retry) and adds the AGit trust gate. It currently flags dreame, whose AGit guard #275 hasn't merged yet.
- **VARIANCE.md** records the move.

**Tests:**
- `shared/tests/release/forgejo-ci.sh` and the new `shared/tests/release/rc-install-matrix.sh` stub curl.
- `macos-scope.sh`'s test gains the macos.yml cases. The old script fails them, and mutations of the new gate (skipped jobs accepted, workflow-name check removed, 403 retried, workflow filter dropped) are each caught.
- The consumers run these through their `tests/release/*.sh` loops.
- Checks run here: pytest, ruff, `tests/test-*.sh`, `shellcheck-all.sh`, the scratch vendor sync. cx review is clean after two rounds of fixes.

**Consumers:** dreame-valetudo and whiskerless re-vendor this once it's tagged, in the PR that moves their macOS gate here.

## forgejo-actions, 2026-11-16T18:18:16-08:00

<!-- ai-review -->
**AI review** of `1d101e3bf0`: Well-structured retirement of GitHub-runner helpers with a solid Forgejo replacement gate. Tests are comprehensive and cover the key failure modes (scoped-out runs, credential refusal, stale checkouts, unclassifiable runs). One pre-existing suggestion remains open; one minor inconsistency in the new test file's permissions.

### Open

- **F1** (suggestion, `shared/packaging/check-forgejo-ci.sh:35`) GITHUB_SERVER_URL fallback can silently point at the wrong host: The server default is `${FORGEJO_CI_SERVER:-${GITHUB_SERVER_URL:-https://forgejo.bryantserver.com}}`. `GITHUB_SERVER_URL` is a GitHub Actions built-in (set to `https://github.com` in every GH-hosted job). If this script is ever invoked in a context where that variable lingers and `FORGEJO_CI_SERVER` is unset, it would query `https://github.com/api/v1/repos/…` (not GitHub's real API host), get a 404 or connection error, retry to the deadline, and blame the run. The failure is fail-closed so no bad release ships, but the diagnosis is misleading. Since the PR's premise is that GitHub runners are retired, the fallback is dead weight; dropping it and keeping only `${FORGEJO_CI_SERVER:-https://forgejo.bryantserver.com}` removes the footgun.
  - Reviewer: Still applies. The PR's own VARIANCE.md entry says "no job in either project runs on GitHub's runners" and the GitHub copies are "read-only mirrors with Actions turned off." A fallback that reads a GitHub-Actions-only variable contradicts that premise and creates a silent misdirection path. One-line fix: `server="${FORGEJO_CI_SERVER:-https://forgejo.bryantserver.com}"`.
- **F2** (suggestion, `shared/tests/release/rc-install-matrix.sh:1`) Test file missing execute bit, inconsistent with siblings: The new test file is created with mode 100644, while every other test in `shared/tests/release/` (including the new `forgejo-ci.sh` in this same PR) is 100755. The documented invocation is `bash "$t"` so it works today, but a consumer that iterates with `"$t"` or a future `shellcheck-all.sh` that checks the exec bit would trip on it. Add the execute bit (`chmod +x`) to match the directory's convention.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJzaGFyZWQvcGFja2FnaW5nL2NoZWNrLWZvcmdlam8tY2kuc2giLCAibGluZSI6IDM1LCAic2V2ZXJpdHkiOiAic3VnZ2VzdGlvbiIsICJzdGF0dXMiOiAib3BlbiIsICJ0aXRsZSI6ICJHSVRIVUJfU0VSVkVSX1VSTCBmYWxsYmFjayBjYW4gc2lsZW50bHkgcG9pbnQgYXQgdGhlIHdyb25nIGhvc3QiLCAiZGV0YWlsIjogIlRoZSBzZXJ2ZXIgZGVmYXVsdCBpcyBgJHtGT1JHRUpPX0NJX1NFUlZFUjotJHtHSVRIVUJfU0VSVkVSX1VSTDotaHR0cHM6Ly9mb3JnZWpvLmJyeWFudHNlcnZlci5jb219fWAuIGBHSVRIVUJfU0VSVkVSX1VSTGAgaXMgYSBHaXRIdWIgQWN0aW9ucyBidWlsdC1pbiAoc2V0IHRvIGBodHRwczovL2dpdGh1Yi5jb21gIGluIGV2ZXJ5IEdILWhvc3RlZCBqb2IpLiBJZiB0aGlzIHNjcmlwdCBpcyBldmVyIGludm9rZWQgaW4gYSBjb250ZXh0IHdoZXJlIHRoYXQgdmFyaWFibGUgbGluZ2VycyBhbmQgYEZPUkdFSk9fQ0lfU0VSVkVSYCBpcyB1bnNldCwgaXQgd291bGQgcXVlcnkgYGh0dHBzOi8vZ2l0aHViLmNvbS9hcGkvdjEvcmVwb3MvXHUyMDI2YCAobm90IEdpdEh1YidzIHJlYWwgQVBJIGhvc3QpLCBnZXQgYSA0MDQgb3IgY29ubmVjdGlvbiBlcnJvciwgcmV0cnkgdG8gdGhlIGRlYWRsaW5lLCBhbmQgYmxhbWUgdGhlIHJ1bi4gVGhlIGZhaWx1cmUgaXMgZmFpbC1jbG9zZWQgc28gbm8gYmFkIHJlbGVhc2Ugc2hpcHMsIGJ1dCB0aGUgZGlhZ25vc2lzIGlzIG1pc2xlYWRpbmcuIFNpbmNlIHRoZSBQUidzIHByZW1pc2UgaXMgdGhhdCBHaXRIdWIgcnVubmVycyBhcmUgcmV0aXJlZCwgdGhlIGZhbGxiYWNrIGlzIGRlYWQgd2VpZ2h0OyBkcm9wcGluZyBpdCBhbmQga2VlcGluZyBvbmx5IGAke0ZPUkdFSk9fQ0lfU0VSVkVSOi1odHRwczovL2Zvcmdlam8uYnJ5YW50c2VydmVyLmNvbX1gIHJlbW92ZXMgdGhlIGZvb3RndW4uIiwgInJlc3BvbnNlIjogIlN0aWxsIGFwcGxpZXMuIFRoZSBQUidzIG93biBWQVJJQU5DRS5tZCBlbnRyeSBzYXlzIFwibm8gam9iIGluIGVpdGhlciBwcm9qZWN0IHJ1bnMgb24gR2l0SHViJ3MgcnVubmVyc1wiIGFuZCB0aGUgR2l0SHViIGNvcGllcyBhcmUgXCJyZWFkLW9ubHkgbWlycm9ycyB3aXRoIEFjdGlvbnMgdHVybmVkIG9mZi5cIiBBIGZhbGxiYWNrIHRoYXQgcmVhZHMgYSBHaXRIdWItQWN0aW9ucy1vbmx5IHZhcmlhYmxlIGNvbnRyYWRpY3RzIHRoYXQgcHJlbWlzZSBhbmQgY3JlYXRlcyBhIHNpbGVudCBtaXNkaXJlY3Rpb24gcGF0aC4gT25lLWxpbmUgZml4OiBgc2VydmVyPVwiJHtGT1JHRUpPX0NJX1NFUlZFUjotaHR0cHM6Ly9mb3JnZWpvLmJyeWFudHNlcnZlci5jb219XCJgLiJ9LCB7ImlkIjogIkYyIiwgImZpbGUiOiAic2hhcmVkL3Rlc3RzL3JlbGVhc2UvcmMtaW5zdGFsbC1tYXRyaXguc2giLCAibGluZSI6IDEsICJzZXZlcml0eSI6ICJzdWdnZXN0aW9uIiwgInN0YXR1cyI6ICJvcGVuIiwgInRpdGxlIjogIlRlc3QgZmlsZSBtaXNzaW5nIGV4ZWN1dGUgYml0LCBpbmNvbnNpc3RlbnQgd2l0aCBzaWJsaW5ncyIsICJkZXRhaWwiOiAiVGhlIG5ldyB0ZXN0IGZpbGUgaXMgY3JlYXRlZCB3aXRoIG1vZGUgMTAwNjQ0LCB3aGlsZSBldmVyeSBvdGhlciB0ZXN0IGluIGBzaGFyZWQvdGVzdHMvcmVsZWFzZS9gIChpbmNsdWRpbmcgdGhlIG5ldyBgZm9yZ2Vqby1jaS5zaGAgaW4gdGhpcyBzYW1lIFBSKSBpcyAxMDA3NTUuIFRoZSBkb2N1bWVudGVkIGludm9jYXRpb24gaXMgYGJhc2ggXCIkdFwiYCBzbyBpdCB3b3JrcyB0b2RheSwgYnV0IGEgY29uc3VtZXIgdGhhdCBpdGVyYXRlcyB3aXRoIGBcIiR0XCJgIG9yIGEgZnV0dXJlIGBzaGVsbGNoZWNrLWFsbC5zaGAgdGhhdCBjaGVja3MgdGhlIGV4ZWMgYml0IHdvdWxkIHRyaXAgb24gaXQuIEFkZCB0aGUgZXhlY3V0ZSBiaXQgKGBjaG1vZCAreGApIHRvIG1hdGNoIHRoZSBkaXJlY3RvcnkncyBjb252ZW50aW9uLiIsICJyZXNwb25zZSI6ICIifV0= -->
