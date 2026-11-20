# #106 ai-review.py: review findings on the 40k output cap and its tests

- Kind: issue, state: open, by cody, created 2026-11-19T10:38:58-08:00
- Labels: status:ready, type:bug; milestone: none

Found by the house review while syncing this script into cody/agents (cody/agents#39), 2026-11-19. The copy there is verbatim, so these belong here:

1. A 40k completion budget plus a prompt that can reach about 70k tokens needs about 110k of served context. If the Studio serves less, a large PR fails as a generic `HTTPError` instead of the explicit cap message. Check the proxy's context limit, or size the cap from it.
2. `tests/test_ai_review_model.py` enters `mock.patch.dict(os.environ, ...)` at import and never exits it. In repos that run this test in one pytest process with other suites, `TOKEN`/`REPO`/`FORGEJO_URL` leak into them. Load the module in `setUpModule` and stop the patcher in `tearDownModule`.
3. `main()`'s `CutOff` branch (status `error`, no retry hint) has no test.
4. Cut-off detection only treats `finish_reason == "length"` as truncated. Any other non-`stop` reason without a `usage` block is parsed as a complete answer.
5. Nits: the comment cites 23,119 reasoning tokens but the fixture uses 23557. And "raise MAX_OUTPUT_TOKENS" above about 53k would trip the 900 s timeout at 59 tok/s.
