# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `LICENSE` (MIT), this changelog, and SPDX licence metadata and project URLs in
  `pyproject.toml`.

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
