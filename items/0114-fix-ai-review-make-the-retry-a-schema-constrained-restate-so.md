# #114 fix(ai-review): make the retry a schema-constrained restate so a review always ends in valid JSON

- Kind: issue, state: closed, by cody, created 2026-11-21T10:31:06-08:00
- Labels: status:in-progress, type:bug; milestone: none

Cody, 2026-11-21: "fix the json thing more robustly".

After #110 the reviewer re-asks once when an answer is unreadable, but the re-ask is another free-form review, so it can fail the same way. On a private repo the first answer had no JSON object; the re-ask happened to work.

Measured on the Studio (oMLX 0.8.2, qwen3.8-flash-next): with `response_format` `json_schema` strict, the grammar is enforced (no Warning header) and applied only after the reasoning, but reasoning is capped at about 4096 tokens (a long derivation stopped at 4094 reasoning tokens and was forced into the schema). Real reviews reason for over 20,000 tokens, so a schema on the review itself would cut its depth.

Plan: keep the first, free review. When its answer cannot be read or checked, the retry gives the model its own first answer (content, and its reasoning when the server returns it) and asks it to restate that review as the JSON object, with a strict `json_schema` matching what `validate` accepts. Restating needs little reasoning, and the grammar makes the shape valid. A server that rejects `response_format` gets the current free re-ask instead. Tests for each path.

Claude has this.

## cody, 2026-11-21T10:45:25-08:00

Done: #115 merged (main 2bb7119). An unreadable review answer is now restated under a strict json_schema, and the first review stays free so it can reason at full depth. It was checked live against the Studio (schema enforced, restate in 5 to 12 s). Next: copy it to a private repo, and to the other repos under #113.
