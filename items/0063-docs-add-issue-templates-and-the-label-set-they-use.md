# #63 docs: add issue templates and the label set they use

- Kind: pull, state: closed, by cody, created 2026-11-17T07:13:16-08:00
- Labels: none; milestone: none
- refs/pull/63/head -> main, merged: True

Closes #61.

- `.forgejo/issue_template/`: bug, feature, decision and spike, the four `docs/adopting.md` asks every project for. A bug carries only `type:bug` (status is set at triage); a feature reminds the filer to set `status:blocked` when it lists a dependency.
- `docs/adopting.md`: points new projects at these templates, lists the label set they and the rules use, and tells existing repos to copy the templates and create the labels too.
- `tools/capability-diff.py`: the issue-template probe only knew `.github/ISSUE_TEMPLATE`, so a repo with Forgejo templates read as missing them. `tests/test_capability_diff.py` fails on main and passes here.

The `type:spike` label was missing here and is now created.

## forgejo-actions, 2026-11-17T07:15:29-08:00

<!-- ai-review -->
**AI review** of `6afbc0df5c`: Clean PR: adds four Forgejo issue templates, updates adopting.md with the label set and template instructions, and fixes the capability-diff probe to recognise `.forgejo/issue_template` alongside `.github/ISSUE_TEMPLATE`. The one-line tool fix is tightly coupled to the feature (without it the new templates are invisible to the probe) and ships with a focused test covering both paths and the absent case.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
