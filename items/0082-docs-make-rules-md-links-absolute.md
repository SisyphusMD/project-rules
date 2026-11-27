# #82 docs: make RULES.md links absolute

- Kind: pull, state: closed, by cody, created 2026-11-17T09:21:48-08:00
- Labels: none; milestone: none
- refs/pull/82/head -> main, merged: True

Closes #77

Every repo carries RULES.md as `.forgejo/RULES.md`, so its relative links (`conventions/`, `conventions/code.md`, `templates/CONTRIBUTING.md`) point at nothing there and fail that repo's doc-link check. They are now reference-style links to the files on main on Forgejo, with a comment at the bottom saying why.

`tests/test_rules_links.py` rejects any relative link in RULES.md (inline, titled or `<...>`), any link to this repo that is not Forgejo (the GitHub copy, a tag, commit or raw URL), and any link to a file here that does not exist. On main's RULES.md it fails with `['conventions/', 'conventions/code.md', 'templates/CONTRIBUTING.md']`. A scratch run with a code-block example, a titled link, an autolink, a GitHub link, a tag link and an issues link showed each caught or allowed as intended. A consumer-style copy now passes `check-doc-links.py --mode tree`.

Repos that already carry the old copy get this when they re-copy it under their adoption issues (#71 to #76).

## forgejo-actions, 2026-11-17T09:22:17-08:00

<!-- ai-review -->
**AI review** of `e9315b05e4`: Clean, focused PR that converts RULES.md's three relative links to absolute Forgejo URLs so consumer copies at .forgejo/RULES.md pass their doc-link check, with a new test that validates link style and target existence. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
