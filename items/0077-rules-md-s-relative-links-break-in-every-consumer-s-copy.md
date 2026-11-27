# #77 RULES.md's relative links break in every consumer's copy

- Kind: issue, state: closed, by cody, created 2026-11-17T08:41:25-08:00
- Labels: status:in-progress, type:bug; milestone: none

Consumers carry RULES.md as .forgejo/RULES.md (rule 22), where its relative links (conventions/, conventions/code.md, templates/CONTRIBUTING.md) point at nothing, so a consumer's doc-link check (packaging/check-doc-links.py) fails as soon as the copy is committed. Found adopting appliance-job-monitor (#73). Make them absolute Forgejo URLs so the copy works anywhere.
