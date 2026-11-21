# #109 AI review fails closed on one transient DNS error

- Kind: issue, state: closed, by cody, created 2026-11-20T00:40:03-08:00
- Labels: status:ready, type:bug; milestone: none

The Review job ends at the first resolver failure and reports a required-check failure: `review failed closed: <urlopen error [Errno -2] Name or service not known>`. Seen three times on 2026-11-19/20 in cody/agents (job 199810 on PR #78, 201150 and 201275 on PR #87); each passed on a plain job rerun with no code change, so it is the runner's DNS, not the review. Rule 14 lists giving up after one transient failure as a bug class. Proposal: retry the model request a bounded number of times with backoff on connection and name-resolution errors only, still failing closed after that, with a test that a first URLError followed by success yields a verdict.

## cody, 2026-11-20T00:41:32-08:00

Narrower than a flaky resolver: every failure came from one runner, id 62383437-3730-3536-3930-313661643039 (cody/agents jobs 199810 first attempt, 201275 twice); reruns on other runners (131bf2ac…, 2760c9f0…, 697f7b66…) resolved studio-llm.forgejo-runner.svc.cluster.local and passed. The service and its endpoints were healthy throughout. So that runner's job containers likely lack cluster DNS (wrong runner, or a non-cluster runner also carrying ubuntu-latest). Identify it (admin runners list) and fix its DNS or labels; the bounded retry is still worth having, but it will not help when every attempt lands on that runner.

## cody, 2026-11-20T08:59:35-08:00

Found it: runner `62383437-…` is annex's CI VM (bryantserver/annex `nix/services/ci-runner.nix`): forgejo-runner 13.2.2 while every cluster pod still runs 13.2.1, and its UUID is the hex of the first 16 characters of its registration secret. It registers with this Forgejo as extra capacity and carries `ubuntu-latest`, but its network fence (by design) has no cluster DNS, so `studio-llm.forgejo-runner.svc.cluster.local` never resolves there.

Fix (Cody chose it 2026-11-20): bryantserver/annex#88 serves the same name and port to the CI VM through annex's Caddy, holding the key outside the VM, so this workflow and every repo's copy stay unchanged. The bounded retry here is still worth doing for real transient blips; it follows once #88 is verified.

## cody, 2026-11-20T09:21:26-08:00

Root cause fixed by bryantserver/annex#89 (verified: a probe on runner `62383437-…` resolves this workflow's unchanged URL and gets a completion). The workflow and its copies need no change. Leaving this issue open for the bounded retry on real transient name/connection errors, which comes next.

## cody, 2026-11-20T12:00:44-08:00

A draft of a transient-error retry for ai-review.py, dropped from #108 to keep that PR to the deadline fix, is saved on the workbench Mac at ~/.local/state/project-rules-109/ai-review-retry-dropped.patch (275 lines, against the pre-#108 script, so it needs rebasing onto 1f037e1). It retries on http.client/urllib connection errors. Use it as a starting point or ignore it; nobody owns this issue yet.
