# #57 Decide whether ci.yml and ai-review.yml need the AGit gate tests.yml has

- Kind: issue, state: open, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:needs-decision, type:decision; milestone: none

From a house-model review on 2026-11-16. tests.yml gates on `flow == 0` (#43) because an AGit PR reports this repo as its head. ci.yml and ai-review.yml are pull_request_target with no such gate, on the same runners, and ai-review holds ISSUE_READ_TOKEN in private repos. They run main's scripts and only read PR files (ruff, yamllint and gitleaks over the head; the model reads the diff), never execute them, which is why this may be fine. Record the reasoning in conventions/shell-and-workflows.md either way, and if a gate is added, make tools/capability-diff.py check the flow half too.

## cody, 2026-11-21T11:45:53-08:00

New input from #116 (2026-11-21): with GitHub sign-up open, an approved outside account can open an AGit PR and edit its description repeatedly. Each opened/edited/synchronize event starts `ai-review.yml` through `pull_request_target` without approval (base workflow), queueing up to 45-minute runs on the Studio model. #117 gates only the comment path. If a gate is added here, the same `github.event.repository.permissions.push` field may work for the PR events too; it is not yet checked on those payloads.
