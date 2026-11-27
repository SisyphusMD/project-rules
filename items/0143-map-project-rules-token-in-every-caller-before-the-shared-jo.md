# #143 Map PROJECT_RULES_TOKEN in every caller before the shared jobs require it

- Kind: issue, state: closed, by cody, created 2026-11-26T20:34:41-08:00
- Labels: type:chore; milestone: none

Part of step 1 in #133; #140 (#136) depends on it.

Trigger: #140 makes the shared `Lint`, `Secrets` and `Review` jobs read the owner's private `.project-rules` manifest with the owner's Actions secret `PROJECT_RULES_TOKEN` (Cody's decision on #133, 2026-11-26). A called workflow sees only the secrets its caller maps in (probed 2026-11-26: an unmapped owner secret arrives empty in the called job, a mapped one arrives whole), and every repo's `ci.yml` and `ai-review.yml` call these jobs at `@main`. If #140 merged first, every repo's required Lint, Secrets and AI review checks would fail closed, including on the PR that fixes its caller.

Order, each step verified before the next:

1. The `project-rules-reader` bot exists with read on each owner's `.project-rules` only (a team per organization, a collaborator under a user), and its token (`read:repository`, plus `read:user` for the repo listing) is every house owner's `PROJECT_RULES_TOKEN`.
2. Every repo that calls the shared jobs maps `PROJECT_RULES_TOKEN` in `ci.yml` (`shared-lint`) and `ai-review.yml` (`shared-review`), as the canonical callers in #140 do. The mapping is harmless before #140: the jobs on `main` ignore it.
3. #140 merges; one consumer PR per owner proves Lint, Secrets and AI review green, each logging the manifest it read.
4. `Owners / The owner manifests can be read and agree` and `Owners / Every repo follows its owner's visibility policy` join this repo's required checks.

Re-copied `issue-archive.yml` files read the secret directly, so they need no caller change.


## cody, 2026-11-26T21:49:29-08:00

Status: steps 1 and 2 done.

1. The `project-rules-reader` bot is a restricted account. It reads each owner's `.project-rules` and nothing else: a read team in each of the three organizations, and read as a collaborator under cody. Checked with its token: all four manifests return 200; private non-manifest repos and a public repo return 404; a write gets 403; each owner's repo listing shows only `.project-rules`. Its token is set as `PROJECT_RULES_TOKEN`: an organization secret on SisyphusMD, bryantserver and humblepixels, and a user secret on cody. The Owners workflow, dispatched from #140's branch, read and checked all four owners with it.
2. Every existing consumer now maps the secret. One PR per repo, each merged with its checks green, its head verified on main and its branch deleted: 6 under SisyphusMD, 6 under bryantserver and 2 under cody (the cody PRs close local issues, since their issue-link check cannot read this repo). No humblepixels repo calls the shared jobs yet.

Since the bot is restricted, the visibility check lists each owner's repos signed out (what the world sees), and rule 21 says that is what it guarantees.

Next: merge #140, run the proof per owner, and make the two Owners checks required.


## cody, 2026-11-26T22:36:19-08:00

Status: done. #140 merged (main 5ac366d); its head is verified on main and the branch is deleted. On main's push, the Owners checks and Tests passed.

Proof per owner: a throwaway PR under each of SisyphusMD, bryantserver, cody and humblepixels called the canonical callers from main. In each, Lint, Secrets and Review logged `owner manifest: <owner>/.project-rules <sha>`, the commit of that owner's current manifest. Lint and Secrets passed; the review ran on the manifest's model and returned findings. The throwaway repos are deleted.

Read anonymously, the public proof's logs held no manifest value and no private repo name. They did name the runner's own internal hosts (the in-cluster git host in actions/checkout, the runner image mirror and the action mirror), as every public repo's job logs on this runner do. That belongs to #142, not to these jobs.

`Owners / The owner manifests can be read and agree (pull_request_target)` and `Owners / Every repo follows its owner's visibility policy (pull_request_target)` are now required on main. The names follow the other checks' pattern; the next PR here will be the first to post them.
