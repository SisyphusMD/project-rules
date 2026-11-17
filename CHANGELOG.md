# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- CI `Secrets` scans only the PR head's history, so issue text copied into the nightly
  `issue-archive` branch no longer fails every PR (#69).
- `SECURITY.md`: vulnerabilities are reported privately to security@bryantserver.com, and
  `templates/SECURITY.md` is the copy every repo carries (#62).
- Rule 9: no AI attribution in commits, pull requests or comments, and the CONTRIBUTING
  template says so (#80). Repos pick it up when they next copy `RULES.md`; an existing
  `CONTRIBUTING.md` takes the line by hand.
- `RULES.md` links to the conventions and the CONTRIBUTING template by absolute URL, so a
  repo's `.forgejo/RULES.md` copy no longer fails its doc-link check (#77).
- `LICENSE` (MIT), this changelog, and SPDX licence metadata and project URLs in
  `pyproject.toml`.
- A Renovate config, so the pins here are updated at all, with every update PR naming the
  standing dependency-updates issue (#67) the issue-link check requires.
- `ci.yml`'s ruff, yamllint and gitleaks pins carry `# renovate:` annotations, and the workflows'
  Python is pinned to an exact `3.15.2`. Repos that copy `ci.yml` pick these up on their next copy.

## [0.3.0] - 2026-11-16

### Changed

- The shared release helpers gate releases on Forgejo's macOS run, and the GitHub-runner helpers
  are gone (#53).
- The gate scripts' comments name this repository as the canonical copy (#52).
- The rules record that projects take contributions on Forgejo (#45).

## [0.2.0] - 2026-11-16

### Added

- The rules, conventions and shared tooling in one public repository, replacing
  bryantserver/project-rules and project-standard.

### Security

- AGit pull requests no longer run on the self-hosted runner: they report this repository as
  their head, so the fork gate let them through (#46).

[Unreleased]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/compare/v0.3.0...main
[0.3.0]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/compare/v0.2.0...v0.3.0
[0.2.0]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/src/tag/v0.2.0
