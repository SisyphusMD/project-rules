# #126 chore(workflows): name the canonical source in mirror-lockdown.yml

- Kind: pull, state: closed, by cody, created 2026-11-24T17:48:55-08:00
- Labels: none; milestone: none
- refs/pull/126/head -> main, merged: True

Refs #78

`mirror-lockdown.yml` lacked the line the other copied workflows carry, so a copy did not say where it comes from. `tests/test_copied_headers.py` finds every copied workflow and fails when one lacks it; it fails on the old file.

This description first had no issue reference, so that the fetched `Issue link` had to fail; that run is the failing proof for #78.

## forgejo-actions, 2026-11-24T17:49:21-08:00

<!-- ai-review -->
**AI review** of `41dd644743`: Clean, minimal PR: adds the canonical-source header to mirror-lockdown.yml and a test that enforces the header on all copied workflows. The earlier F1 finding is withdrawn because `Refs #78` is the correct link for a PR that does part of a multi-PR issue, the gate script explicitly accepts it, and the check passed.

### Withdrawn

- **F1** (blocking, `.github/workflows/mirror-lockdown.yml:3`) PR description lacks `Closes #n` (rule 6): 
  - Reviewer: Withdrawn. Your reasoning is sound: #78 spans multiple PRs, so `Closes` would close it prematurely. `issue-link.py` explicitly accepts `Refs #n`, the `Issue link` check passed on this head, and #125 used the same pattern. The rule's intent—linking the PR to its issue—is satisfied.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICIuZ2l0aHViL3dvcmtmbG93cy9taXJyb3ItbG9ja2Rvd24ueW1sIiwgImxpbmUiOiAzLCAic2V2ZXJpdHkiOiAiYmxvY2tpbmciLCAic3RhdHVzIjogIndpdGhkcmF3biIsICJ0aXRsZSI6ICJQUiBkZXNjcmlwdGlvbiBsYWNrcyBgQ2xvc2VzICNuYCAocnVsZSA2KSIsICJkZXRhaWwiOiAiIiwgInJlc3BvbnNlIjogIldpdGhkcmF3bi4gWW91ciByZWFzb25pbmcgaXMgc291bmQ6ICM3OCBzcGFucyBtdWx0aXBsZSBQUnMsIHNvIGBDbG9zZXNgIHdvdWxkIGNsb3NlIGl0IHByZW1hdHVyZWx5LiBgaXNzdWUtbGluay5weWAgZXhwbGljaXRseSBhY2NlcHRzIGBSZWZzICNuYCwgdGhlIGBJc3N1ZSBsaW5rYCBjaGVjayBwYXNzZWQgb24gdGhpcyBoZWFkLCBhbmQgIzEyNSB1c2VkIHRoZSBzYW1lIHBhdHRlcm4uIFRoZSBydWxlJ3MgaW50ZW50XHUyMDE0bGlua2luZyB0aGUgUFIgdG8gaXRzIGlzc3VlXHUyMDE0aXMgc2F0aXNmaWVkLiJ9XQ== -->

## cody, 2026-11-24T17:50:30-08:00

F1 is wrong: `Closes #78` would close an issue that is not done. #78 stays open through every consumer's switch, so a PR that does part of it names it with `Refs`. `issue-link.py` accepts that (its docstring: "Accepts `Closes #n`, `Fixes #n`, `Resolves #n` or `Refs #n`"), and `CI / Issue link` passed on this head with this description. #125 landed the same way.
