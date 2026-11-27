# #140 feat(gate): read host settings from the owner's .project-rules manifest

- Kind: pull, state: open, by cody, created 2026-11-26T09:52:03-08:00
- Labels: none; milestone: none
- feat/136-read-manifest -> main, merged: False

Closes #136

Trigger: the shared jobs named house-only hosts (gate-lint's package index and gitleaks mirror, review.yml's model endpoint, issue-archive's bot address), so they cannot run on another git host that mirrors project-rules (#133). Now each job reads them from the owner's manifest, `<owner>/.project-rules/env.json`, through `manifest.py` (#134).

What happens now:
- `Lint`, `Secrets`, `Review` and `issue-archive` fetch the gate scripts, then clone the owner's manifest from its `main` with the job token, before any PR checkout, log `owner manifest: <owner>/.project-rules <sha>`, and pass the values on through `$GITHUB_ENV`. The consuming steps use `${PACKAGE_INDEX:?…}`, `${RELEASE_MIRROR:?…}`, `${BOT_EMAIL:?…}`, so an unset value fails the step.
- A missing or invalid manifest fails the job. In the review job it also turns the held `AI review` status into an error saying so, instead of leaving `pending: Starting`.
- `ai_review` exempt: the check passes naming the cited issue, only while the job token or `ISSUE_READ_TOKEN` can read it and it is an open issue. A closed issue fails the check; an unreadable one, or a PR, errors. No policy at all fails closed. A pass already posted stays on its head when the issue later closes, like any other check result.
- House values are unchanged: the three house manifests hold exactly the strings these files had.
- RULES.md: scope is every repository whose owner keeps a manifest; rule 15 allows the exemption; rule 21 takes the backup from the manifest. adopting.md says how an owner gets one.
- Tests workflow: a new job runs the identical read step with this branch's reader, then `manifest.py drift` over the house owners.

Tests that fail on the old code (run against main's workflows and scripts): every read-step copy equals the proven one and runs before any checkout; each job takes its value from the manifest; the review step has no `LLM_URL`; the read step hands values on, fails on a missing or invalid manifest and writes nothing; the cannot-start step posts the error; the exemption cases; `test_no_instance_hosts.py` fails on any instance hostname or cluster-internal service name in `.forgejo/` or `tools/`.

Not merging yet: the bryantserver org is private, so its repos' job tokens cannot read bryantserver/.project-rules (probed: 403 with the token, anonymous fails). Merging now would fail every bryantserver repo's Lint, Secrets and AI review. This waits on that decision. Existing copies of `issue-archive.yml` keep their hardcoded address until they are re-copied.


## forgejo-actions, 2026-11-26T09:58:45-08:00

<!-- ai-review -->
**AI review** of `89f836e540`: Well-implemented PR that moves host-specific settings into the owner's .project-rules manifest, with thorough tests covering the exemption policy, manifest read/handoff, fail-closed behaviour, and a regression guard against instance hostnames. No correctness, security, or test-coverage issues found.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
