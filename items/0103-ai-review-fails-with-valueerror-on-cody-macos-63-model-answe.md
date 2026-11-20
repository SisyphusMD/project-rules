# #103 AI review fails with ValueError on cody/macos#63 (model answer not parseable, every run 3m37s)

- Kind: issue, state: closed, by cody, created 2026-11-19T09:36:27-08:00
- Labels: status:ready, type:bug; milestone: none

cody/macos PR #63 (about 500 changed lines, a Python helper + tests + setup.sh) failed the AI review three times in a row (runs 185526, 185535, 185552). Each run took exactly 3m37s and ended in .forgejo/scripts/ai-review.py raising ValueError while parsing the model's answer (line 182-196: no JSON object / wrong shape), reported as 'Review could not run: ValueError'. Other PRs reviewed fine the same morning, so this looks like a cut-off or malformed answer on a larger diff, perhaps a token or time limit. Next: log the raw answer on parse failure and find the limit.

## cody, 2026-11-19T11:58:03-08:00

Duplicate of #104, which already has Cody's approved fix (40,000-token cap, no retry, usage logged) in PR #105. Same cause on cody/macos#63: replaying its review returned finish_reason=length with all 16,000 tokens spent on reasoning and no content. A parallel retry-without-thinking fix was drafted here and dropped in favour of #104; one idea from it for #104 to consider: put the bounded exception text in the commit status, since 'ValueError' alone hid the cause.
