# #99 Bind published releases to their qualified PR head

- Kind: issue, state: closed, by cody, created 2026-11-17T18:29:31-08:00
- Labels: status:ready, type:bug; milestone: none

During #86 downstream review, found that v0.3.1 checks the final PR tree, but a branch update or an extra push can replace the commit that passed Prepare Release. Preserve and verify the exact original qualification before publishing. Dreame and Whiskerless are adding commit-bound qualification and matching the successful Prepare Release run. Appliance needs the equivalent follow-up. GhostSpectator needs its local PEAK ZIP bound to its prepared source. Cover stale branches, amended PR heads, and retries.
