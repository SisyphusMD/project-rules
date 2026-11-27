# #45 docs: record that both projects take contributions on Forgejo

- Kind: pull, state: closed, by cody, created 2026-11-16T14:08:55-08:00
- Labels: none; milestone: none
- refs/pull/45/head -> main, merged: True

Closes #42

Trigger: the "Contribution routing" entry in VARIANCE.md says whiskerless and dreame-valetudo take issues and pull requests on GitHub, because outside contributors had no Forgejo account. Forgejo now lets anyone sign in with a GitHub account, and the GitHub repositories become read-only mirrors.

Now: the entry records both projects as taking issues and pull requests on Forgejo. A fork pull request still never runs CI by itself; a maintainer reads it and reopens it from a branch in the repository, which runs the suite. Doc-only change (VARIANCE.md, 6 lines changed). Same change as the retired project-standard#36.


Update (2026-11-16, after GitHub sign-in went live):
- The entry now describes the real flow. Accounts wait for activation and can't fork, so pull requests come in as AGit (`refs/for/main`). Forgejo CI skips them behind the `flow == 0` gate. The maintainer moves a change they have read onto a branch here; reopening the AGit pull request isn't how CI gets run.
- `templates/CONTRIBUTING.md` gets the same flow in one sentence.
- Not verified: that an activated outside account can push `refs/for/main`. Cody skipped the test account, so only the push syntax was checked, and that was with a maintainer account on a private repo.

## forgejo-actions, 2026-11-16T14:11:07-08:00

<!-- ai-review -->
**AI review** of `376a14a972`: Doc-only change updating VARIANCE.md and templates/CONTRIBUTING.md to record that both projects now route contributions through Forgejo with AGit pull requests. The change is well-scoped to issue #42 and the content is accurate except for one unverified claim already flagged in the prior review.

### Open

- **F1** (suggestion, `templates/CONTRIBUTING.md:6`) AGit push instructions stated as fact but unverified for outside accounts: The template tells contributors to run `git push origin HEAD:refs/for/main -o topic=<short-name>`, and VARIANCE.md states outside contributors "send AGit pull requests (`refs/for/main`)" as settled fact. The PR description itself notes: "Not verified: that an activated outside account can push `refs/for/main`." Rule 10 says docs state only what the code guarantees. Either verify the flow with an activated outside account before merging, or add a short caveat (e.g. "(not yet confirmed for outside accounts)") so a contributor who hits a permission error knows it is a known gap rather than a mystery.
  - Reviewer: The PR description is transparent about the gap, which is good, but the shipped docs don't carry that caveat. A contributor following the template's instructions and getting a 403 has no way to tell whether they made a mistake or the flow is untested. A one-line parenthetical in the template and a matching note in VARIANCE.md would satisfy rule 10 without blocking the merge.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICJ0ZW1wbGF0ZXMvQ09OVFJJQlVUSU5HLm1kIiwgImxpbmUiOiA2LCAic2V2ZXJpdHkiOiAic3VnZ2VzdGlvbiIsICJzdGF0dXMiOiAib3BlbiIsICJ0aXRsZSI6ICJBR2l0IHB1c2ggaW5zdHJ1Y3Rpb25zIHN0YXRlZCBhcyBmYWN0IGJ1dCB1bnZlcmlmaWVkIGZvciBvdXRzaWRlIGFjY291bnRzIiwgImRldGFpbCI6ICJUaGUgdGVtcGxhdGUgdGVsbHMgY29udHJpYnV0b3JzIHRvIHJ1biBgZ2l0IHB1c2ggb3JpZ2luIEhFQUQ6cmVmcy9mb3IvbWFpbiAtbyB0b3BpYz08c2hvcnQtbmFtZT5gLCBhbmQgVkFSSUFOQ0UubWQgc3RhdGVzIG91dHNpZGUgY29udHJpYnV0b3JzIFwic2VuZCBBR2l0IHB1bGwgcmVxdWVzdHMgKGByZWZzL2Zvci9tYWluYClcIiBhcyBzZXR0bGVkIGZhY3QuIFRoZSBQUiBkZXNjcmlwdGlvbiBpdHNlbGYgbm90ZXM6IFwiTm90IHZlcmlmaWVkOiB0aGF0IGFuIGFjdGl2YXRlZCBvdXRzaWRlIGFjY291bnQgY2FuIHB1c2ggYHJlZnMvZm9yL21haW5gLlwiIFJ1bGUgMTAgc2F5cyBkb2NzIHN0YXRlIG9ubHkgd2hhdCB0aGUgY29kZSBndWFyYW50ZWVzLiBFaXRoZXIgdmVyaWZ5IHRoZSBmbG93IHdpdGggYW4gYWN0aXZhdGVkIG91dHNpZGUgYWNjb3VudCBiZWZvcmUgbWVyZ2luZywgb3IgYWRkIGEgc2hvcnQgY2F2ZWF0IChlLmcuIFwiKG5vdCB5ZXQgY29uZmlybWVkIGZvciBvdXRzaWRlIGFjY291bnRzKVwiKSBzbyBhIGNvbnRyaWJ1dG9yIHdobyBoaXRzIGEgcGVybWlzc2lvbiBlcnJvciBrbm93cyBpdCBpcyBhIGtub3duIGdhcCByYXRoZXIgdGhhbiBhIG15c3RlcnkuIiwgInJlc3BvbnNlIjogIlRoZSBQUiBkZXNjcmlwdGlvbiBpcyB0cmFuc3BhcmVudCBhYm91dCB0aGUgZ2FwLCB3aGljaCBpcyBnb29kLCBidXQgdGhlIHNoaXBwZWQgZG9jcyBkb24ndCBjYXJyeSB0aGF0IGNhdmVhdC4gQSBjb250cmlidXRvciBmb2xsb3dpbmcgdGhlIHRlbXBsYXRlJ3MgaW5zdHJ1Y3Rpb25zIGFuZCBnZXR0aW5nIGEgNDAzIGhhcyBubyB3YXkgdG8gdGVsbCB3aGV0aGVyIHRoZXkgbWFkZSBhIG1pc3Rha2Ugb3IgdGhlIGZsb3cgaXMgdW50ZXN0ZWQuIEEgb25lLWxpbmUgcGFyZW50aGV0aWNhbCBpbiB0aGUgdGVtcGxhdGUgYW5kIGEgbWF0Y2hpbmcgbm90ZSBpbiBWQVJJQU5DRS5tZCB3b3VsZCBzYXRpc2Z5IHJ1bGUgMTAgd2l0aG91dCBibG9ja2luZyB0aGUgbWVyZ2UuIn1d -->
