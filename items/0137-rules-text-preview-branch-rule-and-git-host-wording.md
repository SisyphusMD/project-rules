# #137 Rules text: preview-branch rule and git host wording

- Kind: issue, state: closed, by cody, created 2026-11-26T09:18:33-08:00
- Labels: status:in-progress, type:feature; milestone: none

Step 1 of the build order in #133, part 3 of 3, rules text only. The preview-branch rule from the 2026-11-26 decision on #133 (a repo may name a preview branch in its CONTRIBUTING.md; changes, Renovate's included, land on it through PRs and the required checks, with no direct pushes; main then only takes promotion PRs that pin a commit which passed the preview checks and was approved), folded into rules 6 and 19 so no rule is renumbered, and "git host" instead of Forgejo or forge in the rules text outside the manifest rules (rule 20).

## cody, 2026-11-26T10:05:06-08:00

Status: merged in #139 (merge a425b63b). Rules 6 and 19 carry the preview-branch rule, rule 15 says the checks run from the protected branch a PR targets, rule 20 says git host; adopting.md and the CONTRIBUTING template follow. The AI review's one suggestion (a changelog blank line removed) was the fix for a stray blank line #138 left. Rule 15's long line from this PR is reflowed in #140. Nothing left here.
