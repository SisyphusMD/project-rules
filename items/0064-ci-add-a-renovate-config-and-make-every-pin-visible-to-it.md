# #64 ci: add a Renovate config and make every pin visible to it

- Kind: pull, state: closed, by cody, created 2026-11-17T07:18:13-08:00
- Labels: none; milestone: none
- refs/pull/64/head -> main, merged: True

Closes #60.

The cluster Renovate runs with `requireConfig=required`, so without its own config this repo was skipped and none of its pins ever moved.

- `.renovaterc.json`, ported from the retired project-standard config. Patch, minor and digest updates automerge on green CI.
- Every Renovate PR footer says `Refs #67` (a standing dependency-updates issue), because the issue-link check has no bot exemption.
- The shellcheck image is the one pin in a code file: its PR carries a `No tests:` line for the tests-with-code check and never automerges, since the job that runs the new image is not required.
- gitleaks never automerges either: its PR says to update `GITLEAKS_SHA256`, which Renovate cannot compute. Python bumps wait three days for setup-python's manifest.
- `ci.yml`'s ruff, yamllint and gitleaks pins are annotated; bare `actions/checkout` SHAs get their version comment; `python-version` is the exact `3.15.2` the consumers pin.
- `tests/test_renovate_pins.py`: every SHA pin names its version, every interpreter is exact, every version pin is matched by a Renovate pattern, every code-file pin passes the tests-with-code gate's own regex and does not automerge, and the footer names an issue. The first three fail on main; the automerge assertion fails if the rule is flipped.
- `conventions/shell-and-workflows.md` tells consumers to do the same in their configs.

Not covered: upstream release notes in a Renovate PR body can trip issue-link (#68).

## forgejo-actions, 2026-11-17T07:25:54-08:00

<!-- ai-review -->
**AI review** of `7543666902`: Well-structured PR that adds a Renovate config, annotates every pin so the custom regex managers can find them, pins Python to an exact version, and ships a test that verifies the config's invariants (annotations present, code-file pins gated, footer names an issue). The diff is focused on the single concern of issue #60, docs are updated in the same PR, and the test covers the key failure modes.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
