# #70 fix(ci): scan only the PR head history for secrets (#69)

- Kind: pull, state: closed, by cody, created 2026-11-17T07:51:10-08:00
- Labels: none; milestone: none
- refs/pull/70/head -> main, merged: True

Closes #69

The `Secrets` job ran `gitleaks git` over every ref in a `fetch-depth: 0` clone, which includes `issue-archive` (rule 21). Issue text copied there nightly is not code, and its commits get new SHAs every night, so a `.gitleaksignore` entry can never hold. On a private repo PR #53 it failed on two alembic revision IDs quoted in an old issue.

The job now scans only history reachable from the PR head (`--log-opts=<head sha>`), with the step renamed to match. Ancestors are still scanned, so a secret already on `main` still fails, and allowlists still come from base only.

Proof on gitleaks 8.28.0 (the pinned version):
- Scratch repo: a secret on the PR head is reported; a secret on an unrelated branch is not.
- a private repo clone: the full-ref scan reports the 2 archive hits; the head-only scan is clean.

No tests: workflow YAML has no harness here; the proof above stands in, and the next PR in each consumer runs the new copy (`pull_request_target` runs from `main`).

Consumers with a copy to update: several private repos.

## forgejo-actions, 2026-11-17T07:52:55-08:00

<!-- ai-review -->
**AI review** of `a060d24b00`: Clean, focused fix: the Secrets job now scans only the PR head's history via `--log-opts`, avoiding false positives from the nightly issue-archive branch while still catching secrets in any ancestor (including main). The diff is minimal (one workflow line, one comment, one CHANGELOG entry), the allowlist still comes from base, and the manual proof on gitleaks 8.28.0 is appropriate given no YAML test harness exists in this repo.

### Withdrawn

- **F1** (blocking, `CHANGELOG.md:9`) Rule 7: four independent issues in one PR: The diff as presented contains only two files: .forgejo/workflows/ci.yml (the gitleaks scope change) and one added CHANGELOG.md line for #69. The other CHANGELOG entries visible in context (#62, #77, #80) are pre-existing lines, not additions in this diff. The earlier review ran against a pre-rebase diff where those commits had not yet landed on main.
  - Reviewer: Withdrawn. The author's reply and the actual diff confirm only two files changed; the other issues merged before this rebase.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJDSEFOR0VMT0cubWQiLCAibGluZSI6IDksICJzZXZlcml0eSI6ICJibG9ja2luZyIsICJzdGF0dXMiOiAid2l0aGRyYXduIiwgInRpdGxlIjogIlJ1bGUgNzogZm91ciBpbmRlcGVuZGVudCBpc3N1ZXMgaW4gb25lIFBSIiwgImRldGFpbCI6ICJUaGUgZGlmZiBhcyBwcmVzZW50ZWQgY29udGFpbnMgb25seSB0d28gZmlsZXM6IC5mb3JnZWpvL3dvcmtmbG93cy9jaS55bWwgKHRoZSBnaXRsZWFrcyBzY29wZSBjaGFuZ2UpIGFuZCBvbmUgYWRkZWQgQ0hBTkdFTE9HLm1kIGxpbmUgZm9yICM2OS4gVGhlIG90aGVyIENIQU5HRUxPRyBlbnRyaWVzIHZpc2libGUgaW4gY29udGV4dCAoIzYyLCAjNzcsICM4MCkgYXJlIHByZS1leGlzdGluZyBsaW5lcywgbm90IGFkZGl0aW9ucyBpbiB0aGlzIGRpZmYuIFRoZSBlYXJsaWVyIHJldmlldyByYW4gYWdhaW5zdCBhIHByZS1yZWJhc2UgZGlmZiB3aGVyZSB0aG9zZSBjb21taXRzIGhhZCBub3QgeWV0IGxhbmRlZCBvbiBtYWluLiIsICJyZXNwb25zZSI6ICJXaXRoZHJhd24uIFRoZSBhdXRob3IncyByZXBseSBhbmQgdGhlIGFjdHVhbCBkaWZmIGNvbmZpcm0gb25seSB0d28gZmlsZXMgY2hhbmdlZDsgdGhlIG90aGVyIGlzc3VlcyBtZXJnZWQgYmVmb3JlIHRoaXMgcmViYXNlLiJ9XQ== -->

## cody, 2026-11-17T11:08:54-08:00

F1: the code is correct, the case cannot occur. The diff of this PR is two files: `.forgejo/workflows/ci.yml` (the gitleaks scope) and one `CHANGELOG.md` line. Forgejo agrees: base and merge base are both `ea327b2`, and `pulls/70.diff` lists only those two files. #62, #77 and #80 merged into main (PRs #82, #83, #84) before this rebase; this review ran against the diff from before the rebase, when those commits were not yet on its base.

## cody, 2026-11-17T11:10:16-08:00

Retry: the previous run could not reach the model (URLError); the Studio and the runner proxy answer now. See my reply above about F1: the diff is two files.
