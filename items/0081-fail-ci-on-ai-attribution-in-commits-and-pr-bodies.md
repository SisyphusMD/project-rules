# #81 Fail CI on AI attribution in commits and PR bodies

- Kind: issue, state: open, by cody, created 2026-11-17T09:12:18-08:00
- Labels: status:ready, type:feature; milestone: none

Rule 9 (#80) bans AI attribution in commit messages, PR titles and descriptions. Nothing enforces it: the AI review can only block on a file and line in the diff, and commit messages and the PR body are not in the diff, so an attribution line can only ever be a suggestion.

A `ci.yml` job next to `issue-link` should fail a PR whose title, body or commit messages (base..head) carry a `Co-Authored-By` naming an assistant, a "Generated with" line naming an AI tool, or 🤖. With tests, and proven on a throwaway PR (one pass, one deliberate failure) before it is required, as in `docs/adopting.md`.

Depends on #80.

## cody, 2026-11-17T09:22:33-08:00

Also: the AI review never sees commit messages at all (no commits call in ai-review.py), so a Co-Authored-By trailer is invisible to it, not merely non-blocking. The new job should read `git log base..head` and the PR title and body, shaped like issue-link.py (base commit's copy, fails closed).
