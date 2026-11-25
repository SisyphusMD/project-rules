# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- `gate.yml`, `gate-lint.yml` and `review.yml` hold the gate and AI review jobs for repos to call from project-rules main instead of copying them. Nothing calls them yet: a pilot repo proves them first, then every repo's `ci.yml` and `ai-review.yml` become small callers (#78).
- AI review reads `RULES.md` from project-rules main, with its script, so a rule change applies when
  it merges. A repo drops its `.forgejo/RULES.md` in the change that moves it to the fetched scripts,
  not before: an older reviewer copy still reads it (rule 22, #78).
- `mirror-lockdown.yml` says it is a copy of project-rules' file, as the other copied workflows do (#78).
- The gate jobs (`Issue link`, `Tests with code`, `Diff size`, `AI review`) fetch their scripts from
  project-rules main on every run instead of running the repo's own copy, so a fix reaches every
  repo when it merges and a copy cannot drift. A fetch that fails fails the check (#78).
- `Diff size` reads `.gitattributes` from the base commit only, so a PR cannot mark its own files
  binary to make them count nothing. `Tests with code` also counts tracked executables and `.zsh`
  files as code, and no longer skips a file whose path git quotes (#123).
- AI review: an answer cut off at the output cap before the model wrote any of it (all reasoning)
  is asked once more for the whole review under the answer schema, which bounds the reasoning,
  instead of failing the check with "split the PR or raise MAX_OUTPUT_TOKENS". A second cut-off
  answer fails the check and says so in the comment; one cut off mid-answer still fails closed at
  once, so a finding it had already written cannot be lost (#121).
- AI review: a finding from the first answer that the retry leaves out still counts, a retry cut off
  at its token cap fails the check with the first answer's findings shown instead of an error, and a
  pass after a retry says so in the status (#119).
- AI review: replies on the PR are bounded like the rest of the prompt (each kept to about 4,000
  characters of its start and end, about 30,000 in all, oldest dropped first with a note); a
  blocking finding's line must be a real integer, not `true`, including one carried over from an
  earlier review; the workflow checks out the base commit explicitly without saving credentials,
  and passes `BOT_LOGIN` with the same login its job condition skips (#58).
- AI review: a PR comment starts a review only when its author can push to the repo or wrote the
  PR, so an outside account's comments on PRs no longer queue runs on the review model (#116).
- AI review: the retry of an unreadable answer is now a restate under a strict `json_schema`
  matching what the review accepts, quoting the first answer's text and the end of its reasoning,
  so its shape cannot be wrong; the first review stays unconstrained, since the schema caps
  reasoning near 4,096 tokens. A server that refuses `response_format` gets the free re-ask, and
  an error body without `choices` is retried too (#114).
- AI review: an answer with no JSON or a malformed finding is put back to the model once with the
  error; if the second answer is still bad the check fails, and the comment names what was
  malformed and keeps the well-formed findings of both answers instead of discarding the review.
  An unreadable response envelope gets the same one retry, a retry that succeeds is noted in the
  comment, and the saved state is read from the comment's last marker (#110).
- AI review: a model request that never reached the server (failed name lookup, refused or
  unroutable connection) is retried after 5, 15 and 30 seconds before the review fails closed;
  timeouts and HTTP errors still fail at once (#109).

- AI review: a review now has a 40-minute deadline from its start (`MODEL_DEADLINE_SECONDS`
  can shorten it) and the job a 45-minute limit, so a slow model ends with an error status instead
  of the job being killed with the required check left pending. Any unexpected error, including a
  bad response to the comment write, also sets an error status, and a final status that cannot be
  set fails the job. (#55)
- AI review: the model may generate up to 40,000 tokens (`MAX_OUTPUT_TOKENS` overrides it), since its
  hidden reasoning alone ran past the old 16,000 cap on long reviews; a cut-off answer now fails
  with a status that says to split the PR or raise the cap, and every run logs the model's token
  usage. Reasoning that leaks past a `</think>` the model quoted no longer breaks the verdict
  parse. (#103, #104)
- `RULES.md` allows one scoped sync identity to commit memory notes and indexes
  directly to the designated private memory repository. (#101)
- Provide a shared verifier for the exact commit qualified by Prepare Release. (#99)

## [0.3.1] - 2026-11-17

- Document the two-step stable release flow and verify and tag the exact merged release PR. (#86)
- Tests reject weakened AGit and fork workflow conditions. The CONTRIBUTING template tells
  maintainers how to run the full suite on a branch PR after reviewing the change (#90).
- Release-helper comments describe the current Forgejo build and publication flow (#91).
- `.github/workflows/mirror-lockdown.yml`: a public repo's GitHub copy closes new pull requests
  with a pointer to Forgejo, since GitHub cannot turn them off (#88).
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

[Unreleased]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/compare/v0.3.1...main
[0.3.1]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/compare/v0.3.0...v0.3.1
[0.3.0]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/compare/v0.2.0...v0.3.0
[0.2.0]: https://forgejo.bryantserver.com/SisyphusMD/project-rules/src/tag/v0.2.0
