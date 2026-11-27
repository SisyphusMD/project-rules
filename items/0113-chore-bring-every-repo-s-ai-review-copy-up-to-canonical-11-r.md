# #113 chore: bring every repo's AI review copy up to canonical (11 repos still on 9369e1a)

- Kind: issue, state: closed, by cody, created 2026-11-21T08:56:01-08:00
- Labels: status:in-progress, type:chore; milestone: none

After #112, an audit of every non-archived repo on forgejo.bryantserver.com found these carrying `.forgejo/scripts/ai-review.py` exactly as canonical 9369e1a, with neither the connect retry (#109) nor the malformed-answer re-ask (#110): several private repos, SisyphusMD/appliance-job-monitor, SisyphusMD/archiver, SisyphusMD/dreame-valetudo, SisyphusMD/GhostSpectator, SisyphusMD/homebrew-tap, SisyphusMD/whiskerless. a private repo is handled in a private repo.

Plan: one issue and one PR per repo copying `ai-review.py` (and the `ISSUE_READ_TOKEN` line in `ai-review.yml` where missing), unchanged from canonical. Other copied CI files are left as they are, because some repos have local hardening that canonical lacks (a private repo's `ci.yml`, `diff-size.py` and `tests-with-code.py`). Nothing keeps copies in sync today, so they drift silently; that gap is worth its own decision.

Claude has this.

## cody, 2026-11-21T09:03:10-08:00

Plan correction from a private repo: do not add the `ISSUE_READ_TOKEN` env line by rote. Some repos keep the issue reader disabled on purpose (a private repo asserts a `disabled-for-cody-macos` sentinel in `tests.yml`), and the line would hand the sentinel to the reviewer as a token. Copy the script, and add the line only where the repo actually wants the reader. qx also flagged two canonical points that fail closed but are worth a look: an `{"error": ...}` or list reply from the model server raises KeyError/TypeError and skips the re-ask, and the timing comment above `MAX_OUTPUT_TOKENS` still sizes one answer, though a review can now make two.

## cody, 2026-11-21T17:23:13-08:00

From #58 (PR #118, pending merge): along with `ai-review.py`, each copy needs two targeted `ai-review.yml` edits, made by hand since repos carry local differences. (1) On the `actions/checkout` step, `with: ref: ${{ github.sha }}` and `persist-credentials: false`. (2) `BOT_LOGIN: forgejo-actions` in the review step env, the same login the job condition skips. Canonical tests: `tests/test_ai_review_model.py` class `ReviewWorkflow`. Copy only after #118 is merged.

## cody, 2026-11-21T20:29:57-08:00

Copies of canonical 64b857c (with the #118 checkout pin and BOT_LOGIN, and the #119 re-ask fixes) are merged in 11 of 12 repos:
- homebrew-tap: #24 (PR #24 open; merging next)
- a private repo: PR 95, merged 14d3fdc
- a private repo: PR 369, merged 7750acb
- a private repo: PR 83, merged 5873cd8
- a private repo: PR 2665, merged 380681890
- appliance-job-monitor: PR 30, merged 104e205
- archiver: PR 382, merged fbec42e
- dreame-valetudo: PR 320, merged af09cd9
- GhostSpectator: PR 39, merged 0ca1734
- whiskerless: PR 248, merged 1ca91af
- a private repo: PR 94, merged cb94678

The script in each is byte-for-byte canonical. ai-review.yml is canonical where the repo's file matched the old canonical; otherwise the repo's own file got the two #118 edits by hand. No ISSUE_READ_TOKEN line was added anywhere, and a private repo keeps its disabled sentinel.

Held: a private repo. Its own copy of test_ai_review_model.py expects the old IndexError/AttributeError where canonical now raises named ValueErrors, so the copy needs that test updated too. Waiting on Cody.

Gap found: several private repos still use the older job `if:`, without the "commenter can push or wrote the PR" gate. That needs its own follow-up.

## cody, 2026-11-22T17:39:35-08:00

a private repo is now on 64b857c (a private repo via #213). With that, all 12 repos carry the canonical review script.

## cody, 2026-11-22T17:43:34-08:00

Canonical moved to 72f8fcc (#122, #121: retry a reasoning-only cut-off under the schema). a private repo is being copied now in a private repo because #2688 was stuck on it. The other 11 repos (several private repos, appliance-job-monitor, archiver, dreame-valetudo, GhostSpectator, homebrew-tap, whiskerless) are one version behind again; a private repo also carries its own copy of the tests.

## cody, 2026-11-22T21:55:06-08:00

Correction to the 2026-11-21 "Gap found" note: several private repos are private, and #116 kept the older comment `if:` in private repos on purpose (outside accounts cannot see or comment on them). Not a gap. Issues opened for it in each repo (several private repos) are closed with that reason; nothing changed.

## cody, 2026-11-23T18:47:23-08:00

a private repo is on canonical 72f8fcc: a private repo via PR 102, merged e3eb01d. Script byte-for-byte canonical; ai-review.yml unchanged (private-repo gate kept). Its own review passed after one retry. (Claude, a private repo session.)

## cody, 2026-11-23T22:05:29-08:00

All 12 repos are on canonical 72f8fcc (script byte-for-byte, checked on each main). several private repos were done earlier. The other ten, each with its own issue and PR, merged and verified 2026-11-23:
- a private repo: issue 233, PR 234. Its trimmed test copy gained the canonical classification tests, plus get_result tests showing a reasoning-only cut-off retries under the schema and a mid-answer one does not.
- a private repo: issue 383, PR 385
- a private repo: issue 85, PR 86
- a private repo: issue 103, PR 104 (the Studio apply it starts is checked separately)
- appliance-job-monitor: issue 31, PR 32
- archiver: issue 384, PR 385
- dreame-valetudo: issue 328, PR 329
- GhostSpectator: issue 40, PR 41
- homebrew-tap: issue 25, PR 26
- whiskerless: issue 252, PR 253

ai-review.yml was unchanged everywhere. Found along the way: qx review returns an empty answer when the reviewed code quotes think tags (a private repo). Cody asked whether these copies should share code instead. That is #78; its direction is waiting on his answer. (Claude, studio-status session.)

## cody, 2026-11-24T21:10:37-08:00

Done, and superseded: every repo listed here reached 72f8fcc, and none carries a copy of the review script any more. They run project-rules main's (#78, which stays open for the workflow files). Closing.
