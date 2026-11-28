# #146 feat(gate): add a Copies match check

- Kind: pull, state: closed, by cody, created 2026-11-27T07:13:27-08:00
- Labels: none; milestone: none
- refs/pull/146/head -> main, merged: True

Adds a `Copies match` job to the shared gate. On every PR it compares the repo's own copies with project-rules main and fails when one has fallen behind:

- **The ci.yml, ai-review.yml and issue-archive.yml callers:** compared line by line, ignoring comments. Allowed differences, per docs/adopting.md: a dropped ISSUE_READ_TOKEN mapping, the repo's own Lint and Secrets in place of shared-lint, other jobs of its own, and one preview branch beside main in ci.yml.
- **Issue templates:** the `name` and `labels` front matter must match; prompts may be reworded.
- **`mirror-lockdown.yml`:** public repos only, byte for byte.
- **Retired copies:** `.forgejo/scripts/issue-archive.py` must be gone.

Each repo checks only its own checkout: no token, no other repo, nothing private in a public log. project-rules compares its PR head with itself. This replaces the nightly cross-repo job first planned on #141 (Cody's decision recorded there).

Not required yet. Per docs/adopting.md it is proven on real PRs first, and making it required is a rule-15 change for its own issue.

Order: merge after the issue-archive caller rollout lands in every repo, so the check starts green. A dry run of the script against every house repo's main shows only the issue-archive swap that rollout makes.

Closes #141


## forgejo-actions, 2026-11-27T07:33:54-08:00

<!-- ai-review -->
**AI review** of `8cde0bc2fa`: Well-implemented and thoroughly tested addition of a `Copies match` gate job that compares each repo's copied files against project-rules main. The script logic, fork guard, allowed-exception handling, and test coverage all look correct and complete.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
