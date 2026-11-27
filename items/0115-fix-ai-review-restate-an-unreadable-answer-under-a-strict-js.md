# #115 fix(ai-review): restate an unreadable answer under a strict json_schema

- Kind: pull, state: closed, by cody, created 2026-11-21T10:42:02-08:00
- Labels: none; milestone: none
- refs/pull/115/head -> main, merged: True

Closes #114

When the first review's answer can't be read or checked, the retry is now a restate instead of a second free review. The model gets its own rejected answer back (its text, and the end of its reasoning when the server returns it) and answers under a strict `json_schema` that mirrors what `validate` accepts, so the grammar rules out a wrong shape.

The first review stays unconstrained. Measured on the Studio, oMLX caps reasoning near 4,096 tokens under a schema (a long derivation stopped at 4,094), and reviews reason for over 20,000.

Also:
- a reply with no `choices` (a server error body) is a named ValueError and gets the retry, while a KeyError or TypeError from a broken script or setup still fails as an error, not as a malformed answer;
- a server that refuses `response_format` (a 400 or 422 that names the schema) gets the free re-ask, and any other 400, such as an over-long prompt, fails as before;
- the schema retry is capped at 16,000 output tokens, so both calls fit the deadline;
- long text is clipped keeping its start and end.

Checked live against the Studio (oMLX 0.8.2):
- the restate turned a prose-only rejected answer into a valid blocking finding in 5 to 12 seconds with 63 to 144 reasoning tokens;
- the schema is enforced with no Warning header (a requested severity `major` came back `suggestion`, and a blank id was forced to contain visible characters).

Tests: 17 new or changed; the new ones fail against the old script.

## forgejo-actions, 2026-11-21T10:44:24-08:00

<!-- ai-review -->
**AI review** of `52b25643ce`: The PR cleanly implements the schema-constrained restate described in #114: the retry quotes the rejected answer's text and reasoning tail, sends a strict json_schema mirroring validate's contract, falls back to a free re-ask when the server refuses response_format, and handles server-error bodies as unreadable rather than script errors. Tests cover every new path (schema sent, schema refused, 400-for-other-reason, choices missing, clip, output cap, end-to-end restate) and the diff is well within size limits.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
