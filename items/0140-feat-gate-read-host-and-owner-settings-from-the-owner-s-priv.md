# #140 feat(gate): read host and owner settings from the owner's private .project-rules manifest

- Kind: pull, state: closed, by cody, created 2026-11-26T09:52:03-08:00
- Labels: none; milestone: none
- refs/pull/140/head -> main, merged: True

Closes #136

Depends on #143.

Trigger: the shared jobs named house-only hosts (gate-lint's package index and gitleaks mirror, review.yml's model endpoint, issue-archive's bot address), so they cannot run on another git host that mirrors project-rules (#133). Now each job reads them from the owner's private manifest, `<owner>/.project-rules/env.json`, through `manifest.py` (#134).

What happens now:
- `Lint`, `Secrets`, `Review` and `issue-archive` fetch the gate scripts, then clone the owner's manifest from its `main` with the owner's read-only `PROJECT_RULES_TOKEN`, before any PR checkout, log `owner manifest: <owner>/.project-rules <sha>`, and pass the values on through `$GITHUB_ENV`. The consuming steps use `${PACKAGE_INDEX:?…}`, `${RELEASE_MIRROR:?…}`, `${BOT_EMAIL:?…}`, so an unset value fails the step. The canonical callers map the secret in; nothing else of the caller's is handed over.
- No token, a missing or an invalid manifest fails the job, with a message that names no host and no value. In the review job it also turns the held `AI review` status into an error, instead of leaving `pending: Starting`.
- `ai_review` exempt: the check passes naming the cited issue, only while it can be read and is an open issue. A closed issue fails the check; an unreadable one, or a PR, errors. No policy at all fails closed. A pass already posted stays on its head when the issue later closes, like any other check result.
- Schema: owner keys `visibility`, `mirrors` (replaces `mirror_url`), `decided_by`, `bot_email`; host keys `llm_url`, `ai_review`, `package_index`, `release_mirror`. Drift compares host keys only.
- House values are unchanged for the jobs: the house manifests hold the same package index, release mirror and model endpoint these files had. Each owner's archive committer is now its own noreply address.
- RULES.md: scope is every repository whose owner keeps a manifest; rule 2 takes the deciders from it, rule 15 allows the exemption, rule 21 takes the mirrors and visibility from it. adopting.md says how an owner gets a manifest and the reader bot, and how to rotate its token.
- New `Owners` workflow (this repo only, on `pull_request_target`, push, nightly and dispatch, so PR code never runs with the token): the identical read step and handoff check, `manifest.py drift` over the owners on this git host, and every owner's repos against its visibility policy. Public repos that break a private policy are named; private ones only counted.

Tests that fail on the old code: every read-step copy equals the proven one, reads with `PROJECT_RULES_TOKEN` and runs before any checkout; a missing token fails before trying; each job takes its value from the manifest; the review step has no `LLM_URL`; the read step hands values on, fails on a missing or invalid manifest without printing the URL and writes nothing; the cannot-start step posts the error; the exemption cases; the new schema, drift and visibility cases, none echoing a value; `test_no_instance_hosts.py` fails on any instance hostname or cluster-internal service name in `.forgejo/` or `tools/`.

Not merging yet: #143 (the reader bot and its secrets, then every caller mapping the secret) must land first, or every repo's Lint, Secrets and AI review would fail closed.

Large diff: the reader, every job that reads it, the callers that map its token, the Owners checks that prove it on the real manifests, and the rules text describing it land together, since any one alone fails closed or describes behaviour that is not there.


## forgejo-actions, 2026-11-26T09:58:45-08:00

<!-- ai-review -->
**AI review** of `ab334249e8`: The PR moves all host-specific settings from hardcoded values in shared workflows to the owner's private `.project-rules` manifest, with comprehensive tests, proper fail-closed behaviour, and no leaked values in error messages. The two earlier findings are resolved by the rewritten `problem()` function and the added non-string mirrors test case.

### Resolved

- **F1** (suggestion, `.forgejo/scripts/manifest.py:53`) `id(pattern)` dict lookup is fragile for future pattern additions: The code now uses an explicit `pattern is EMAIL` / `pattern is NAMES` / else chain instead of the `id(pattern)` dict lookup, making the mapping impossible to miss when a key is added.
- **F2** (suggestion, `tests/test_manifest.py:62`) No test for a non-string element in the mirrors list (branch-coverage gap): The parametrized invalid-manifest test now includes `({"mirrors": ["https://a.example", 7]}, "mirrors must be a list of distinct URLs")`, covering the `isinstance(v, str)` False branch.


Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W3siaWQiOiAiRjEiLCAiZmlsZSI6ICIuZm9yZ2Vqby9zY3JpcHRzL21hbmlmZXN0LnB5IiwgImxpbmUiOiA1MywgInNldmVyaXR5IjogInN1Z2dlc3Rpb24iLCAic3RhdHVzIjogInJlc29sdmVkIiwgInRpdGxlIjogImBpZChwYXR0ZXJuKWAgZGljdCBsb29rdXAgaXMgZnJhZ2lsZSBmb3IgZnV0dXJlIHBhdHRlcm4gYWRkaXRpb25zIiwgImRldGFpbCI6ICJUaGUgY29kZSBub3cgdXNlcyBhbiBleHBsaWNpdCBgcGF0dGVybiBpcyBFTUFJTGAgLyBgcGF0dGVybiBpcyBOQU1FU2AgLyBlbHNlIGNoYWluIGluc3RlYWQgb2YgdGhlIGBpZChwYXR0ZXJuKWAgZGljdCBsb29rdXAsIG1ha2luZyB0aGUgbWFwcGluZyBpbXBvc3NpYmxlIHRvIG1pc3Mgd2hlbiBhIGtleSBpcyBhZGRlZC4iLCAicmVzcG9uc2UiOiAiIn0sIHsiaWQiOiAiRjIiLCAiZmlsZSI6ICJ0ZXN0cy90ZXN0X21hbmlmZXN0LnB5IiwgImxpbmUiOiA2MiwgInNldmVyaXR5IjogInN1Z2dlc3Rpb24iLCAic3RhdHVzIjogInJlc29sdmVkIiwgInRpdGxlIjogIk5vIHRlc3QgZm9yIGEgbm9uLXN0cmluZyBlbGVtZW50IGluIHRoZSBtaXJyb3JzIGxpc3QgKGJyYW5jaC1jb3ZlcmFnZSBnYXApIiwgImRldGFpbCI6ICJUaGUgcGFyYW1ldHJpemVkIGludmFsaWQtbWFuaWZlc3QgdGVzdCBub3cgaW5jbHVkZXMgYCh7XCJtaXJyb3JzXCI6IFtcImh0dHBzOi8vYS5leGFtcGxlXCIsIDddfSwgXCJtaXJyb3JzIG11c3QgYmUgYSBsaXN0IG9mIGRpc3RpbmN0IFVSTHNcIilgLCBjb3ZlcmluZyB0aGUgYGlzaW5zdGFuY2Uodiwgc3RyKWAgRmFsc2UgYnJhbmNoLiIsICJyZXNwb25zZSI6ICIifV0= -->
