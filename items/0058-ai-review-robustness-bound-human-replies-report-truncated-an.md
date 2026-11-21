# #58 AI review robustness: bound human replies, report truncated answers, pin the checkout ref

- Kind: issue, state: open, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:ready, type:chore; milestone: none

From a house-model review on 2026-11-16: (1) ai-review.py interpolates human reply bodies uncapped, while everything else in the prompt is capped; cap them, oldest dropped first. (2) ask_model ignores finish_reason, so a length cut shows up as a JSON parse error; name the cause. (3) ai-review.yml's checkout has no ref and no persist-credentials: false, unlike ci.yml; pin the base sha explicitly. Smaller: workflows declare no permissions, checkout pins lack version comments and renovate markers, ai-review.yml hardcodes forgejo-actions while BOT_LOGIN is configurable, a bool passes the line-number check, and a closed PR keeps a stale status. Coverage for the gate scripts is #9.

## cody, 2026-11-20T00:12:26-08:00

Status (2026-11-20, session rotating):
- The public Forgejo 500 was a LAN hairpin artifact: Anubis had no client address for LAN clients reaching the WAN address. Outside visitors were never affected. Fixed in bryantserver/k8s#2617 (merged 437fb4325, deployed and verified): login, release JSON, bottle and blueprint downloads all return 200 through the public address.
- Next: the four forgejo-defaults PRs, one at a time: appliance-job-monitor #21, dreame-valetudo #306, whiskerless #228, archiver #364. Their changes are still uncommitted in the worktrees and each branch is behind main.
- Still open after that: archiver maintenance patch proof and GhostSpectator PEAK proof (#74, #75, #86). No public releases are authorized.


## cody, 2026-11-20T08:52:05-08:00

Forgejo-defaults batch landed 2026-11-20: appliance-job-monitor #26 (3f1fcc4), dreame-valetudo #314 (00b77aa), whiskerless #242 (b4b6e99), archiver #369 (5a59992). Each merged serially with all contexts green, mirror tips verified, branches and worktrees pruned, issues #21/#306/#228/#364 closed. A bench-only IPv6 403 seen in review is the agents-personal Cilium policy lacking anubis-forgejo: bryantserver/k8s#2640. Still open and blocked: #74, #75, #86 (Archiver maintenance proof, GhostSpectator PEAK proof, as before).

## cody, 2026-11-20T15:37:53-08:00

Rule-18 cleanup done with Cody's approval (2026-11-20). The six negative-proof branches were deleted with leases on their recorded tips (none had an open PR): Appliance, Dreame, Whiskerless, GhostSpectator and Archiver `proof/required-check-failures` (b0bf6ef, 2040943, ea52e5b, 7f3c7a4, 8203dfb) and Tap `tap/dreame-valetudo/v999.0.0/formula` (799f8d2). Annex and GitHub mirrors verified clear. The proof evidence stays in the per-repo receipts.

Also: bryantserver/k8s#2640 (bench egress to the Anubis proxies) fixed by k8s#2646 and verified live.

Still open: #74, #75, #86, blocked on the separately authorized Archiver maintenance and GhostSpectator PEAK proofs.
