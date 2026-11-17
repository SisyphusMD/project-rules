# #58 AI review robustness: bound human replies, report truncated answers, pin the checkout ref

- Kind: issue, state: open, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:ready, type:chore; milestone: none

From a house-model review on 2026-11-16: (1) ai-review.py interpolates human reply bodies uncapped, while everything else in the prompt is capped; cap them, oldest dropped first. (2) ask_model ignores finish_reason, so a length cut shows up as a JSON parse error; name the cause. (3) ai-review.yml's checkout has no ref and no persist-credentials: false, unlike ci.yml; pin the base sha explicitly. Smaller: workflows declare no permissions, checkout pins lack version comments and renovate markers, ai-review.yml hardcodes forgejo-actions while BOT_LOGIN is configurable, a bool passes the line-number check, and a closed PR keeps a stale status. Coverage for the gate scripts is #9.
