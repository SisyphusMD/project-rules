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

0. **The owner's manifest**: an owner's first repo needs a private `<owner>/.project-rules` on the
   same git host, with an `env.json` that `python3 -I .forgejo/scripts/manifest.py check env.json`
   accepts. Owner keys: `visibility` (`"public"` or `"private"`: what its repos may be),
   `mirrors` (the push-mirror URLs), `decided_by` (rule 2's deciders, such as `"Cody and Anna"`)
   and `bot_email` (the owner's noreply committer address). Host keys, copied from another owner
   on that host, since this repo's `Owners` check fails when they differ: `llm_url`,
   `package_index`, `release_mirror` and `ai_review` (`"required"`, or
   `{"exempt": "owner/repo#n"}` citing the open issue that brings the review back, rule 15). Add
   the owner to `OWNERS` in this repo's `owners.yml`.
   - **The manifest reader**: the jobs read the manifest with the `project-rules-reader` bot's
     token, never the job token, which cannot read another private repo. The bot has no other
     access: in an organization it is the only member of a `project-rules-reader` team with read
     on `.project-rules` alone; under a user it is a read collaborator on `.project-rules`. The
     owner keeps its token as the Actions secret `PROJECT_RULES_TOKEN` (an organization secret, or
     a user secret for a user), and the callers map it in.
   - **Rotating it**: the token is `read:repository`, `read:user` and `read:organization` (the
     visibility check lists repos), named for the date it was minted. Sign
     in as the bot (its credentials are in the house secret store), mint a new one, set it as
     every owner's `PROJECT_RULES_TOKEN`, dispatch this repo's `Owners` workflow and check it reads
     each owner, then delete the old token. A leaked token reads only the manifests and public repos.
1. **Mirror**: a push mirror to each of the manifest's `mirrors` and the nightly `issue-archive` branch (rule 21).
   A public repo also copies [`mirror-lockdown.yml`](../.github/workflows/mirror-lockdown.yml)
   to `.github/workflows/`, and its GitHub copy has Actions on, limited to that one action, with
   a read-only default token.
2. **Workflows**: copy this repo's `.forgejo/` workflows except `tests.yml`, `owners.yml`, `gate.yml`,
   `gate-lint.yml` and `review.yml`, its issue templates and `scripts/issue-archive.py` in, and
   create the labels listed above. `ci.yml` and `ai-review.yml` are only callers: their jobs run
   from this repo's `main` (`gate.yml`, `gate-lint.yml`, `review.yml`), and so do the gate scripts
   and the `RULES.md` the AI review reads; the jobs and `issue-archive.yml` take the package
   index, release mirror, model endpoint and bot address from the owner's manifest, read with `PROJECT_RULES_TOKEN`. A repo whose secret `ISSUE_READ_TOKEN` is not a
   read:issue token drops that mapping from both callers rather than hand the jobs something else.
   A repo with its own Lint and Secrets jobs keeps them and drops the `shared-lint` call, so no
   check name is posted twice. Whatever lands on this repo's `main` runs as trusted code in every
   such repo's `pull_request_target` runs, with that repo's job token.
3. **`SECURITY.md`** from [the template](../templates/SECURITY.md), so a vulnerability is reported
   privately rather than in a public issue.
4. **`CONTRIBUTING.md`**: how its tests run, what counts as a test, its safety-critical code,
   its own required checks and its break-glass steps.
5. **Protect `main`**, and a preview branch if the repo names one (rule 6), whose name then also
   goes in `ci.yml`'s `pull_request_target` branches (Forgejo runs the callers from the branch
   a PR targets, so the preview branch carries them too), once the workflows are on it: no direct
   pushes, admins included, branch up to date, 0 approvals, and every required check from the
   rules with the exact context name Forgejo reports (`CI / <job> (pull_request_target)`, `AI review`). Never require the
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
