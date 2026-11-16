# Contributing

This repo holds the rules, and follows them: [RULES.md](RULES.md). Issues and pull requests are
opened on Forgejo. A rule change is a pull request that closes an issue here, with the
maintainer's decision recorded on that issue.

## Tests

- **Run them**: `python3 -m pytest tests/` and `for t in tests/test-*.sh; do bash "$t"; done`.
- **Safety-critical code** (100% coverage): the gate scripts in `.forgejo/scripts/`, because a
  bug there lets a pull request past a rule in every repo, and `tools/vendor.py` and
  `tools/check.py`, because a bug there lets a vendored copy drift unnoticed.
- `shared/tests/release/` runs inside a consumer (it needs that consumer's `packaging/project.env`),
  not here.

## Required checks

The standard set from the rules, plus the `Tests` workflow: lint and unit tests, shell scripts, and
a scratch vendor that `tools/check.py` must report in sync.

## Break-glass

As in the rules.
