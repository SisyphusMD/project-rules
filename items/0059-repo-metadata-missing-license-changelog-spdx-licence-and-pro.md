# #59 Repo metadata missing: LICENSE, CHANGELOG, SPDX licence and project URLs

- Kind: issue, state: closed, by cody, created 2026-11-17T06:50:12-08:00
- Labels: status:ready, type:chore; milestone: none

conventions/code.md sections 5 and 7 require a LICENSE, the licence and its reasoning in CONTRIBUTING.md, a Keep a Changelog CHANGELOG.md with an Unreleased section, SPDX licence metadata and machine-readable project URLs. This repo has none of them, though every consumer does.

Licence: MIT. Files here are vendored into MIT (whiskerless, appliance-job-monitor) and GPL-3.0 (dreame-valetudo) projects, so they must be usable under both; a permissive licence is the only one that is.
