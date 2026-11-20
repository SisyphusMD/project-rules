# #109 AI review fails closed on one transient DNS error

- Kind: issue, state: open, by cody, created 2026-11-20T00:40:03-08:00
- Labels: status:ready, type:bug; milestone: none

The Review job ends at the first resolver failure and reports a required-check failure: `review failed closed: <urlopen error [Errno -2] Name or service not known>`. Seen three times on 2026-11-19/20 in cody/agents (job 199810 on PR #78, 201150 and 201275 on PR #87); each passed on a plain job rerun with no code change, so it is the runner's DNS, not the review. Rule 14 lists giving up after one transient failure as a bug class. Proposal: retry the model request a bounded number of times with backoff on connection and name-resolution errors only, still failing closed after that, with a test that a first URLError followed by success yields a verdict.

## cody, 2026-11-20T00:41:32-08:00

Narrower than a flaky resolver: every failure came from one runner, id 62383437-3730-3536-3930-313661643039 (cody/agents jobs 199810 first attempt, 201275 twice); reruns on other runners (131bf2ac…, 2760c9f0…, 697f7b66…) resolved studio-llm.forgejo-runner.svc.cluster.local and passed. The service and its endpoints were healthy throughout. So that runner's job containers likely lack cluster DNS (wrong runner, or a non-cluster runner also carrying ubuntu-latest). Identify it (admin runners list) and fix its DNS or labels; the bounded retry is still worth having, but it will not help when every attempt lands on that runner.
