# #138 feat(gate): add the owner manifest reader and schema check

- Kind: pull, state: closed, by cody, created 2026-11-26T09:24:55-08:00
- Labels: none; milestone: none
- refs/pull/138/head -> main, merged: True

Closes #134

Trigger: #133 moves the house-only values out of the shared workflows into a per-owner manifest, `<owner>/.project-rules/env.json`. This adds the script that reads it; nothing calls it yet, so no job changes.

`.forgejo/scripts/manifest.py`:
- `check FILE...` validates a manifest (the manifest repos can run it too).
- `env FILE` validates and prints `KEY=value` lines for `$GITHUB_ENV`: `AI_REVIEW`, `AI_REVIEW_EXEMPT`, `MIRROR_URL`, `LLM_URL`, `PACKAGE_INDEX`, `RELEASE_MIRROR`, `BOT_EMAIL`.
- `drift FILE...` fails when owners disagree on a key the git host shares (everything but `ai_review`).

No defaults: the tests reject a missing or unknown key, a repeated key (json would let the last `ai_review` win), `ai_review` other than `"required"` or `{"exempt": "owner/repo#n"}`, and any value with whitespace, a newline or quotes, so a value cannot add a line to `$GITHUB_ENV` or an argument to a command. `llm_url` may be left out only by an exempt owner. 100% branch coverage on the script.

The three house manifests (SisyphusMD, bryantserver, cody) already exist with today's values and pass `check` and `drift`.

## forgejo-actions, 2026-11-26T09:26:01-08:00

<!-- ai-review -->
**AI review** of `725d711cdd`: Clean, well-tested addition of the owner manifest reader/schema-check script. The validation is strict (no defaults, rejects injection vectors), branch coverage appears complete for all paths in the script, and the tests exercise every error case described in the PR. No issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
