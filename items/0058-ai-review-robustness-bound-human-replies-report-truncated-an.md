# #58 AI review robustness: bound human replies, report truncated answers, pin the checkout ref

- Kind: issue, state: closed, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:in-progress, type:chore; milestone: none

From a house-model review on 2026-11-16: (1) ai-review.py interpolates human reply bodies uncapped, while everything else in the prompt is capped; cap them, oldest dropped first. (2) ask_model ignores finish_reason, so a length cut shows up as a JSON parse error; name the cause. (3) ai-review.yml's checkout has no ref and no persist-credentials: false, unlike ci.yml; pin the base sha explicitly. Smaller: workflows declare no permissions, checkout pins lack version comments and renovate markers, ai-review.yml hardcodes forgejo-actions while BOT_LOGIN is configurable, a bool passes the line-number check, and a closed PR keeps a stale status. Coverage for the gate scripts is #9.

## cody, 2026-11-20T00:12:26-08:00

Status (2026-11-20, session rotating):
- The public Forgejo 500 was a LAN hairpin artifact: Anubis had no client address for LAN clients reaching the WAN address. Outside visitors were never affected. Fixed in a private repo (merged 437fb4325, deployed and verified): login, release JSON, bottle and blueprint downloads all return 200 through the public address.
- Next: the four forgejo-defaults PRs, one at a time: appliance-job-monitor #21, dreame-valetudo #306, whiskerless #228, archiver #364. Their changes are still uncommitted in the worktrees and each branch is behind main.
- Still open after that: archiver maintenance patch proof and GhostSpectator PEAK proof (#74, #75, #86). No public releases are authorized.


## cody, 2026-11-20T08:52:05-08:00

Forgejo-defaults batch landed 2026-11-20: appliance-job-monitor #26 (3f1fcc4), dreame-valetudo #314 (00b77aa), whiskerless #242 (b4b6e99), archiver #369 (5a59992). Each merged serially with all contexts green, mirror tips verified, branches and worktrees pruned, issues #21/#306/#228/#364 closed. A bench-only IPv6 403 seen in review is the agents-personal Cilium policy lacking anubis-forgejo: a private repo. Still open and blocked: #74, #75, #86 (Archiver maintenance proof, GhostSpectator PEAK proof, as before).

## cody, 2026-11-20T15:37:53-08:00

Rule-18 cleanup done with Cody's approval (2026-11-20). The six negative-proof branches were deleted with leases on their recorded tips (none had an open PR): Appliance, Dreame, Whiskerless, GhostSpectator and Archiver `proof/required-check-failures` (b0bf6ef, 2040943, ea52e5b, 7f3c7a4, 8203dfb) and Tap `tap/dreame-valetudo/v999.0.0/formula` (799f8d2). Backup and GitHub mirrors verified clear. The proof evidence stays in the per-repo receipts.

Also: a private repo (bench egress to the Anubis proxies) fixed by a private repo and verified live.

Still open: #74, #75, #86, blocked on the separately authorized Archiver maintenance and GhostSpectator PEAK proofs.

## cody, 2026-11-21T11:35:57-08:00

Claude (session "AI review robustness #58") has this, on branch fix/58-ai-review-robustness. Coordinated with the #113 owner, who will carry it into the copies after merge.

## cody, 2026-11-21T17:23:07-08:00

Technical call: Of the smaller items: no workflow permissions: block (Forgejo reportedly ignores it, unverified on 17.0.2, and a wrong scope would break the required check everywhere); checkout pins already carry version comments, which Renovate reads; a closed PR keeps its last status, since it cannot merge and reopening re-runs the review. Why: Each either has no effect on Forgejo, is already met, or has no failure mode. The rest of #58 is PR #118.

Decided by: Claude, 2026-11-21.

## cody, 2026-11-21T17:25:28-08:00

Done (2026-11-21): PR #118 merged as 0e929cc. Ancestry is verified, a private repo and GitHub mirrors are at 0e929cc, and the branch is pruned everywhere. Replies are bounded in the prompt, a blocking finding needs an exact int line (saved findings too), BOT_LOGIN is stated in the workflow with parity tests, and the checkout is pinned to github.sha with persist-credentials: false. Live check: reply-path run 42418 fetched 0e929cc by SHA with the new step and passed. The pull_request_target path will be confirmed on the next project-rules PR; run 41970 already showed github.sha is main there. The smaller items are recorded as decisions above. Copies into other repos: #113 (comment there lists the two ai-review.yml edits).

## cody, 2026-11-21T19:06:51-08:00

Verified live on pull_request_target: the AI review of PR #120 (run 42470, job 206783, PR head 1d49b9b) used the pinned checkout. It fetched main's bare commit (`fetch ... origin 0e929ccfc1ee`), then ran `checkout --force 0e929cc`; HEAD is 0e929cc, the #118 merge, not the PR head. (An earlier homebrew-tap run proved nothing: pull_request_target runs main's workflow, which there still has the unpinned step.)

## cody, 2026-11-22T08:37:12-08:00

pull_request_target side of the pinned checkout is now verified live: #120 review run 42470 fetched main 0e929cc by bare SHA (the new step) rather than its PR head 1d49b9b, and passed. Both trigger paths are proven (reply path: run 42418).
