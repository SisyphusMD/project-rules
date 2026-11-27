# #121 fix(ai-review): reasoning alone can use the whole output cap, so a small PR can never get a review

- Kind: issue, state: closed, by cody, created 2026-11-22T12:42:59-08:00
- Labels: status:in-progress; milestone: none

a private repo (7 files, +296/-30) failed the AI review three times on 2026-11-22 (job rerun, then a reply). Each run stopped at about 4.5 minutes with `completion_tokens: 40000`, all of them `reasoning_tokens`, on a 14.7k-token prompt (qwen3.8-flash-next). The status says "split the PR or raise MAX_OUTPUT_TOKENS", but the PR is already small, so splitting it would not help.

The reviewer needs a way out when the model reasons past the cap without answering. Options: a separate reasoning budget or lower reasoning effort, or one retry that asks for the answer with reasoning capped. Raising the cap alone only moves the limit.

Blocks: a private repo (required `AI review` context).

## cody, 2026-11-22T17:23:47-08:00

Claude (session c2478d45) has this; Cody asked for the fix 2026-11-22.

## cody, 2026-11-22T17:43:33-08:00

Status: fixed in #122, merged as 72f8fcc. An answer cut off before any of its text is asked once more for the whole review under the answer schema; one cut off mid-answer still fails closed; a second cut-off fails with both errors shown. Codex review caught two fail-open risks in the first draft (a "stop reasoning" retry could pass an unfinished review, and a mid-answer cut-off could drop a written finding); both fixed before merge. The a private repo copy is a private repo (PR #2691), which unblocks a private repo. The other repos copies are tracked on #113.
