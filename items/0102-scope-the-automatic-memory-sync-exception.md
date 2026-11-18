# #102 Scope the automatic memory sync exception

- Kind: pull, state: closed, by cody, created 2026-11-17T22:54:18-08:00
- Labels: none; milestone: none
- refs/pull/102/head -> main, merged: True

Closes #101.

An automated update to a memory note needs to reach the other machines without a pull request for each write. This adds an exception for the scoped sync identity in one designated private repository. It limits direct pushes to memory notes and indexes, with path validation and a credential scan before each push. Tools, workflows, hooks, settings, and instructions use the ordinary issue and pull request process.

The local unit suite, shell tests, lint checks, and scratch vendoring check passed.

## forgejo-actions, 2026-11-17T22:55:36-08:00

<!-- ai-review -->
**AI review** of `87146d6ad4`: The PR adds a scoped exception to RULES.md for automatic memory sync in a designated private repository, matching the maintainer's decision in #101. The diff is small, focused, and includes a CHANGELOG entry. The earlier finding F1 misread the diff and should be withdrawn.

### Withdrawn

- **F1** (suggestion, `RULES.md:120`) Exception text says "workflows" where the decision says "scripts": The finding claimed the PR substituted "workflows" for "scripts" and dropped "shared" from "shared settings." Re-reading the actual diff, the exception text reads "tools, scripts, workflows, hooks, shared or local settings, and instructions" — it contains both "scripts" and "workflows," and retains "shared." The PR is slightly broader than the decision (adding "workflows" and "or local"), which makes the exception narrower (more items require a PR), so it is more conservative than what was decided and creates no security gap.
  - Reviewer: Withdrawing: the factual claims in the original finding are incorrect. The diff includes both "scripts" and "workflows" (not a substitution), and "shared" is present in "shared or local settings" (not dropped). The additions beyond the decision's list make the exception more restrictive, not less, so there is no scope mismatch that could let something through.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJSVUxFUy5tZCIsICJsaW5lIjogMTIwLCAic2V2ZXJpdHkiOiAic3VnZ2VzdGlvbiIsICJzdGF0dXMiOiAid2l0aGRyYXduIiwgInRpdGxlIjogIkV4Y2VwdGlvbiB0ZXh0IHNheXMgXCJ3b3JrZmxvd3NcIiB3aGVyZSB0aGUgZGVjaXNpb24gc2F5cyBcInNjcmlwdHNcIiIsICJkZXRhaWwiOiAiVGhlIGZpbmRpbmcgY2xhaW1lZCB0aGUgUFIgc3Vic3RpdHV0ZWQgXCJ3b3JrZmxvd3NcIiBmb3IgXCJzY3JpcHRzXCIgYW5kIGRyb3BwZWQgXCJzaGFyZWRcIiBmcm9tIFwic2hhcmVkIHNldHRpbmdzLlwiIFJlLXJlYWRpbmcgdGhlIGFjdHVhbCBkaWZmLCB0aGUgZXhjZXB0aW9uIHRleHQgcmVhZHMgXCJ0b29scywgc2NyaXB0cywgd29ya2Zsb3dzLCBob29rcywgc2hhcmVkIG9yIGxvY2FsIHNldHRpbmdzLCBhbmQgaW5zdHJ1Y3Rpb25zXCIgXHUyMDE0IGl0IGNvbnRhaW5zIGJvdGggXCJzY3JpcHRzXCIgYW5kIFwid29ya2Zsb3dzLFwiIGFuZCByZXRhaW5zIFwic2hhcmVkLlwiIFRoZSBQUiBpcyBzbGlnaHRseSBicm9hZGVyIHRoYW4gdGhlIGRlY2lzaW9uIChhZGRpbmcgXCJ3b3JrZmxvd3NcIiBhbmQgXCJvciBsb2NhbFwiKSwgd2hpY2ggbWFrZXMgdGhlIGV4Y2VwdGlvbiBuYXJyb3dlciAobW9yZSBpdGVtcyByZXF1aXJlIGEgUFIpLCBzbyBpdCBpcyBtb3JlIGNvbnNlcnZhdGl2ZSB0aGFuIHdoYXQgd2FzIGRlY2lkZWQgYW5kIGNyZWF0ZXMgbm8gc2VjdXJpdHkgZ2FwLiIsICJyZXNwb25zZSI6ICJXaXRoZHJhd2luZzogdGhlIGZhY3R1YWwgY2xhaW1zIGluIHRoZSBvcmlnaW5hbCBmaW5kaW5nIGFyZSBpbmNvcnJlY3QuIFRoZSBkaWZmIGluY2x1ZGVzIGJvdGggXCJzY3JpcHRzXCIgYW5kIFwid29ya2Zsb3dzXCIgKG5vdCBhIHN1YnN0aXR1dGlvbiksIGFuZCBcInNoYXJlZFwiIGlzIHByZXNlbnQgaW4gXCJzaGFyZWQgb3IgbG9jYWwgc2V0dGluZ3NcIiAobm90IGRyb3BwZWQpLiBUaGUgYWRkaXRpb25zIGJleW9uZCB0aGUgZGVjaXNpb24ncyBsaXN0IG1ha2UgdGhlIGV4Y2VwdGlvbiBtb3JlIHJlc3RyaWN0aXZlLCBub3QgbGVzcywgc28gdGhlcmUgaXMgbm8gc2NvcGUgbWlzbWF0Y2ggdGhhdCBjb3VsZCBsZXQgc29tZXRoaW5nIHRocm91Z2guIn1d -->
