# Bringing a repo under these rules

## A new project

1. Settle the plan with the maintainer, one question at a time.
2. Create the repo with a README saying what the project is, `docs/plan.md`, `docs/decisions/`,
   issue templates (feature, spike, decision, bug) and a `CONTRIBUTING.md` from
   [the template](../templates/CONTRIBUTING.md).
3. Create the labels and milestones, file one pinned "plan and decision log" issue with every
   planning decision as a comment, and split the plan into issues with dependencies.
4. Bring it in as below.

## An existing repo

1. **Mirror**: the backup-forge push mirror and the nightly `issue-archive` branch (rule 21).
2. **Workflows**: copy this repo's `.forgejo/` workflows and scripts in, and `RULES.md` as
   `.forgejo/RULES.md`: the AI review reads the rules from there, since it cannot follow a link.
3. **`CONTRIBUTING.md`**: how its tests run, what counts as a test, its safety-critical code,
   its own required checks and its break-glass steps.
4. **Protect `main`** once the workflows are on it: no direct pushes, admins included, branch
   up to date, 0 approvals, and every required check from the rules with the exact context
   name Forgejo reports (`CI / <job> (pull_request_target)`, `AI review`). A
   `pull_request_target` workflow does not run on the PR that adds it, so prove each new check
   on the next PR, one passing run and one deliberate failure, before requiring it. A
   misnamed required check blocks every PR.
5. Leave `issue-archive` unprotected: Forgejo refuses the Actions token's push to a protected
   branch, and the branch is regenerated nightly.
6. **Vendoring**, for a project that ships releases: run `tools/vendor.py` against it, write its
   `packaging/project.env`, and add `python3 packaging/check-standard-sync.py` to its CI.
