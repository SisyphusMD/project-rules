# Contributing

This repo holds the rules, and follows them: [RULES.md](RULES.md). Issues and pull requests are
opened on Forgejo. A rule change is a pull request that closes an issue here, with the
maintainer's decision recorded on that issue.

The `Tests` workflow on main skips AGit and fork pull requests. A maintainer
reads the change, pushes it to a branch here and opens a pull request from
that branch to run the whole suite. CI and AI review use the workflows on
main and read the proposed changes as data. See #79 for the limits of the
gate when a pull request carries a different workflow.

## Tests

- **Run them**: Install pytest and PyYAML at the versions in
  [tests.yml](.forgejo/workflows/tests.yml), then run
  `python3 -m pytest tests/` and `for t in tests/test-*.sh; do bash "$t"; done`.
- **Safety-critical code** (100% coverage): the gate scripts in `.forgejo/scripts/`, because a
  bug there lets a pull request past a rule in every repo, and `tools/vendor.py` and
  `tools/check.py`, because a bug there lets a vendored copy drift unnoticed.
- `shared/tests/release/` runs inside a consumer (it needs that consumer's `packaging/project.env`),
  not here.

## Required checks

The standard set from the rules, plus the `Tests` workflow: lint and unit tests, shell scripts, a
fetch of the gate scripts as every repo's CI does it, and a scratch vendor that `tools/check.py`
must report in sync. Every repo runs the gate from this `main`, so a branch pull request with a
failing test never merges (#132); an AGit or fork pull request skips all four, so it goes through
the maintainer flow above.

## Releases

Consumers pin a tag (`STANDARD.lock`, `release-pins.env`), so a release is a tag on `main`. In the
pull request before it, move the `Unreleased` entries in `CHANGELOG.md` under the new version and
set the same version in `pyproject.toml`; tag `vX.Y.Z` once it merges. A test holds the two files
to the same version, and the tag's Tests run checks the tag against them.

## Break-glass

As in the rules.

## License

MIT. The consumers are the SisyphusMD projects, which copy files from `shared/` and `.forgejo/`
into their own trees: whiskerless and appliance-job-monitor are MIT, dreame-valetudo is
GPL-3.0-or-later. A vendored file has to sit under either licence without changing it, and only a
permissive licence does that; MIT matches the majority of the consumers. Anyone adopting these
rules for their own project copies them the same way, so the same reasoning holds for them. No
third-party code ships here: CI only runs third-party tools and images, pinned, and links none.
