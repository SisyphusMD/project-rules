# #1 Plan and decision log

- Kind: issue, state: open, by cody, created 2026-11-16T14:07:18-08:00
- Labels: type:decision; milestone: none

_Recreated from bryantserver/project-rules#1 (issue, opened by cody on 2026-11-16)._

Decisions for the house project rules, one per comment. Moved here from bryantserver/casa#38, where the playbook and skill were first written (cody/agents 04291e7).

## cody, 2026-11-16T14:07:18-08:00

_cody, 2026-11-16 06:49:_

Decision: The rules live in their own repo, bryantserver/project-rules, not in cody/agents or any project's README. Repos carry them as enforced settings (branch protection, required checks) plus a short CONTRIBUTING-style file that points here and adds only repo-specific notes. Why: Centralized so the rules are not lost or copied out of date; Casa is just the first repo following them.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:18-08:00

_cody, 2026-11-16 06:49:_

Decision: The upstream small-teaching mode (small chunks, Cody approving every commit and PR) does not carry over yet, maybe one day. Only the upstream craft rules do: smallest correct diff, one concern per PR, every hunk maps to the issue, regression tests proven to fail first, declared checks run, docs in the same PR. CI and the AI review are the gate. Why: Per-PR approval would stall merges while Cody is away; the craft rules are what keep diffs reviewable.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:18-08:00

_cody, 2026-11-16 06:52:_

Decision: Every repo follows these rules; there is no list of following repos. Repos still being brought in are tracked as issues, not as a manifest. Why: Eventually all repos follow it.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:19-08:00

_cody, 2026-11-16 06:52:_

Decision: Every repo has a push mirror on annex (forgejo.lan), and that is a rule here, checked like the others. Why: The annex copy is how a repo survives losing the cluster Forgejo.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:19-08:00

_cody, 2026-11-16 07:23:_

Technical call: Diff size limit is 400 changed lines, not counting tests, lockfiles and generated files; over it needs `Large diff: <reason>` in the PR description, judged by the AI review, rather than a warning-only check. Why: Casa's largest PR so far was 291 lines; a stated reason is cheap for a legitimate big diff, while a bare warning gets ignored. Cody asked whether it should be soft (2026-11-16); revisit if it blocks real work.

Decided by: agent, 2026-11-16.

## cody, 2026-11-16T14:07:19-08:00

_cody, 2026-11-16 13:25:_

Decision: Outside contributors come in through Forgejo for every public repo; the GitHub copies become mirrors only. Why: One place where the rules and checks apply to everyone, outside contributors included.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:19-08:00

_cody, 2026-11-16 13:52:_

Decision: The rules move to a new public repo, SisyphusMD/project-rules, created from scratch (no transfer or git merge). Its first commit is written by hand and folds in SisyphusMD/project-standard, expanded from the two converged siblings to every public repo. The history of both repos is recreated as issues; then bryantserver/project-rules and SisyphusMD/project-standard are deleted. Why: One public rulebook every contributor can read, with a clean history.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:20-08:00

_cody, 2026-11-16 13:52:_

Decision: Leave the Forgejo account name as is; hiding the real name is not possible (login and past commits). Rules text says 'the maintainer'; other people's names stay out of everything public. Why: The name is already public in past commits and the login.

Decided by: Cody, 2026-11-16.

## cody, 2026-11-16T14:07:20-08:00

_cody, 2026-11-16 13:52:_

Technical call: Public repos get no ISSUE_READ_TOKEN: they read cross-repo issues unauthenticated only. The new repo is built private and made public only on Cody's yes, after a scan of its tree and recreated issues. Why: issue-link prints the linked issue's title in CI logs and the AI review posts from linked issue text, both public in a public repo; private issue content would leak.

Decided by: agent, 2026-11-16.

## cody, 2026-11-16T14:07:20-08:00

_cody, 2026-11-16 13:57:_

Decision: Coverage stays at 99% branch coverage overall and 100% on safety-critical code in every repo; project-standard's measure-first rule is replaced. Why: One strict, simple bar every repo is held to.

Decided by: Cody, 2026-11-16.
