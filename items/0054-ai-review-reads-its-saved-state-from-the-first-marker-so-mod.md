# #54 AI review reads its saved state from the first marker, so model-echoed text can wipe carried findings

- Kind: issue, state: open, by cody, created 2026-11-16T19:37:16-08:00
- Labels: status:ready, type:bug; milestone: none

From a house-model review on 2026-11-16, confirmed on main: ai-review.py:243 takes STATE_RE.search (first match), while render() writes the real state line last, after model-supplied finding text that is not escaped. A forged `<!-- ai-review-state ... -->` echoed into a finding comes first and replaces prior, so open blocking findings are forgotten on the next run. Fix: take the last match (or put the state line first) and escape `<!--` in model strings. Test: a body with a forged marker ahead of the real one keeps the real state.
