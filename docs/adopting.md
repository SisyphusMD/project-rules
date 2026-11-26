# Bringing a repo under these rules

## A new project

1. Settle the plan with the maintainer, one question at a time.
2. Create the repo with a README saying what the project is, `docs/plan.md`, `docs/decisions/`,
   issue templates (feature, spike, decision, bug: copy [this repo's](../.forgejo/issue_template/)),
   a `CONTRIBUTING.md` from [the template](../templates/CONTRIBUTING.md) and a `SECURITY.md` from
   [its template](../templates/SECURITY.md).
3. Create the labels and milestones, file one pinned "plan and decision log" issue with every
   planning decision as a comment, and split the plan into issues with dependencies. The labels
   the templates and the rules use: `type:feature`, `type:spike`, `type:decision`, `type:bug`,
   `type:chore`, `status:needs-decision`, `status:ready`, `status:in-progress`, `status:blocked`.
   Forgejo drops a template label the repo does not have, so create them before the first issue.
4. Bring it in as below.

## An existing repo

1. **Mirror**: the backup-forge push mirror and the nightly `issue-archive` branch (rule 21).
   A public repo also copies [`mirror-lockdown.yml`](../.github/workflows/mirror-lockdown.yml)
   to `.github/workflows/`, and its GitHub copy has Actions on, limited to that one action, with
   a read-only default token.
2. **Workflows**: copy this repo's `.forgejo/` workflows except `tests.yml`, `gate.yml`,
   `gate-lint.yml` and `review.yml`, its issue templates and `scripts/issue-archive.py` in, and
   create the labels listed above. `ci.yml` and `ai-review.yml` are only callers: their jobs run
   from this repo's `main` (`gate.yml`, `gate-lint.yml`, `review.yml`), and so do the gate scripts
   and the `RULES.md` the AI review reads. A repo whose secret `ISSUE_READ_TOKEN` is not a
   read:issue token drops that mapping from both callers rather than hand the jobs something else.
   A repo with its own Lint and Secrets jobs keeps them and drops the `shared-lint` call, so no
   check name is posted twice. Whatever lands on this repo's `main` runs as trusted code in every
   such repo's `pull_request_target` runs, with that repo's job token.
3. **`SECURITY.md`** from [the template](../templates/SECURITY.md), so a vulnerability is reported
   privately rather than in a public issue.
4. **`CONTRIBUTING.md`**: how its tests run, what counts as a test, its safety-critical code,
   its own required checks and its break-glass steps.
5. **Protect `main`** once the workflows are on it: no direct pushes, admins included, branch
   up to date, 0 approvals, and every required check from the rules with the exact context
   name Forgejo reports (`CI / <job> (pull_request_target)`, `AI review`). Never require the
   calling jobs' own checks (`CI / shared-gate`, `AI review / shared-review` and so on): one passes
   when the jobs it calls are skipped. A
   `pull_request_target` workflow does not run on the PR that adds it, so prove each new check
   on the next PR, one passing run and one deliberate failure, before requiring it. A
   misnamed required check blocks every PR. Set up [releases from protected main](releasing.md)
   before blocking direct pushes on a repository that publishes releases.
6. Leave `issue-archive` unprotected: Forgejo refuses the Actions token's push to a protected
   branch, and the branch is regenerated nightly.
7. **Vendoring**, for a project that ships releases: run `tools/vendor.py` against it, write its
   `packaging/project.env`, and add `python3 packaging/check-standard-sync.py` to its CI.
