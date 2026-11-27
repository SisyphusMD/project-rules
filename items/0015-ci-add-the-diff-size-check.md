# #15 ci: add the Diff size check

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:25-08:00
- Labels: pr-record; milestone: none

_Recreated from bryantserver/project-rules#15 (pull request, opened by cody on 2026-11-16, merged 2026-11-16). Branch `refs/pull/15/head` into `main`._

Closes #14
Refs #2

Rule 8 set a 400-line limit, but nothing enforced it. New `Diff size` job: it sums added and deleted lines from `git diff --numstat base...head`, skipping test paths (same definition as Tests with code) and lockfiles, and fails over 400 unless the description has `Large diff: <reason>`. It runs main's copy of the script, so a PR cannot raise its own limit. Renames count only their edits; a rename from code into `tests/` still counts, so moving code into a test path is not a way around it. Rule 8 now says "tests and lockfiles": generated code goes through the `Large diff:` reason instead of an exclusion a PR could claim for itself.

Tests (`tests/test_diff_size.py`, 8): code counted, tests and lockfiles not; deletions counted; pure rename 0; rename into tests counted; binary 0; exactly 400 passes; 401 fails; 401 with a reason passes; an empty reason fails. Checked they fail with the rename rule or the test filter broken. CONTRIBUTING.md gets the test command.

This job does not run on this PR (main's ci.yml has no such job yet). It becomes a required check after the next PR shows it passing.

## cody, 2026-11-16T14:07:25-08:00

_cody, 2026-11-16 08:16:_

Re-running the review: the first attempt failed closed on a DNS lookup of the LLM proxy (`Name or service not known`), not on the PR.

## cody, 2026-11-16T14:07:25-08:00

_forgejo-actions, 2026-11-16 08:17:_

**AI review** of `0a20ccf629`: Clean, well-tested CI gate for the 400-line diff-size rule. The script correctly parses `git diff --numstat -M -z` output (including renames and binary files), the base-commit script extraction prevents self-escalation, and the 8 tests cover the key behaviours (code vs. tests/lockfiles, deletions, rename-into-tests, binary, boundary, override, empty-reason). No correctness, security, or test-coverage gaps found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
