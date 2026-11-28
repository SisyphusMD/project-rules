# #152 fix(gate): fetch project-rules with the job token

- Kind: pull, state: closed, by cody, created 2026-11-27T11:35:51-08:00
- Labels: none; milestone: none
- refs/pull/152/head -> main, merged: True

Closes #151

Every "Fetch the gate scripts" step now clones project-rules with the job token. The header comes from the environment through `git --config-env`, so it stays out of the clone URL, argv (which `GIT_TRACE2` records), the log and `.git/config`. The step fails with a plain message if no job token is set. Hosts that allow anonymous reads keep working, since the token can read a public repo.

- gate.yml (all four jobs, Copies match included), gate-lint.yml (Lint and Secrets), review.yml, archive.yml and the tests.yml copy change together. owners.yml has no fetch step.
- test_gate_fetch.py now holds the gate-lint copies equal too. It clones over smart HTTP from a local `git http-backend` that refuses a request without the right header, and it checks that neither the token nor its encoded form shows up in the output, git's trace or the clone's config.
- archive.yml's push step is unchanged: it still sets its own header for the caller's issue-archive branch.

Review: `cx review` flagged the `-c` argv being visible in git trace output, and that the file:// test never proved the header reached a server. Both are fixed here.


## forgejo-actions, 2026-11-27T11:39:16-08:00

<!-- ai-review -->
**AI review** of `fd2f0f9fa4`: Clean, well-scoped fix for #151: every 'Fetch the gate scripts' step now authenticates with the job token via `git --config-env` so the credential stays out of argv, the clone URL, logs, and `.git/config`. The test suite is upgraded from a `file://` clone to a real smart-HTTP server that rejects requests without the correct header, and it asserts the token never leaks into output, trace, or config. All copies are held equal, including the newly added gate-lint ones.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
