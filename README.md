# project-rules

How SisyphusMD projects are run, and the shared tooling that holds them to it.

| Path | What |
| --- | --- |
| [RULES.md](RULES.md) | The rules every repo follows: issues, pull requests, tests, review, merge |
| [conventions/](conventions/) | How code, tests and docs are written: [code](conventions/code.md) for every project, then [Python](conventions/python.md), [shell and workflows](conventions/shell-and-workflows.md), and the [converged siblings](conventions/siblings.md) |
| [VARIANCE.md](VARIANCE.md) | The recorded, deliberate differences between the two converged siblings, whiskerless and dreame-valetudo |
| [docs/adopting.md](docs/adopting.md) | Bringing a repo under these rules |
| [templates/CONTRIBUTING.md](templates/CONTRIBUTING.md) | The `CONTRIBUTING.md` each repo starts from |
| `.forgejo/` | The checks every repo runs on a pull request (issue link, tests with code, diff size, lint, secrets, AI review) and the nightly issue archive; repos carry copies |
| `shared/`, `tools/` | Release and packaging helpers vendored into consumers, and the tools that vendor them and check for drift |

Decisions about the rules are comments on issue #1. A rule change is a pull request here that
closes an issue.

## Vendoring

Shared files are **vendored**: physically copied and committed into each consumer, with
`STANDARD.lock` recording the source tag and every file's SHA-256. There is deliberately **no
submodule, no runtime fetch, and no cross-repo package.** A three-year-old tag of a consumer must
still build and release with this repository unreachable.

```bash
# Update a consumer to the current standard
python3 tools/vendor.py ../whiskerless

# What a consumer runs in CI (stdlib only, no network)
python3 tools/check.py .
```

**Never improve a shared helper by editing the vendored copy.** Change it here, re-vendor every
consumer, land them together. `tools/check.py` fails when a copy is edited in place, which is the
failure that drove two projects apart: someone improves a helper in one repo, the sibling never
learns about it, and a year later there are four divergent behaviours across two files that
started identical. `changelog-section.sh` had drifted into two versions, each better in ways the
other was not:

| From | Improvement the sibling was missing |
|---|---|
| Dreame | fails loudly when the version heading is absent, instead of emitting empty release notes |
| Dreame | stops at any `## ` heading, not only bracketed ones |
| Whisk | strips the leading blank line |
| Whisk | stops at link-reference definitions, which a Keep a Changelog file collects at the foot |

### Per-project parameters

`packaging/project.env` holds each project's own values and is **not** vendored or locked:

```bash
PROJECT_REPO_SLUG="SisyphusMD/whiskerless"
PROJECT_TAP_SLUG="SisyphusMD/homebrew-tap"
```

`packaging/asset-roles.sh` is the other per-project file: the release's asset table, which
`reconcile-releases.sh`, `prune-rcs.sh` and `wait-for-release.sh` read. It declares `_ASSET_ROLES`
and `_IGNORED_ASSETS`, and may declare `_OPTIONAL_ASSET_ROLES` (roles an older release predates,
which the wait does not demand of it) and `_OPTIONAL_ASSET_PREDECESSORS` (what such a release
carries in their place, which the wait then demands instead).

A project that needs only part of the standard lists the paths it takes, on one line, and must
include `packaging/check-standard-sync.py`. Without the line it takes everything. Removing a path
from the list retires it on the next vendor, and an unknown or malformed entry stops the vendor
before anything is written.

```bash
STANDARD_FILES="packaging/check-standard-sync.py packaging/changelog-section.sh"
```

### Adding a file to the standard

1. It must be genuinely project-agnostic, or parameterised through `project.env`.
2. Merge the **union** of every consumer's version: assume each side knows something the other
   does not, because so far each side always has.
3. Test it against every consumer's real data before vendoring.
4. Re-vendor every consumer, land together.

## Testing

```bash
python3 -m pytest tests/          # the gate scripts and the vendoring tools
for t in tests/test-*.sh; do bash "$t"; done   # the release helpers, network-free
```

The release-helper tests cover the guards that must hold *before* any request goes out, chiefly
the tag validator, whose output is interpolated straight into URL paths, so it refuses traversal,
injection, whitespace and malformed versions. They also pin the safe defaults:
`REL_REPLACE_POLICY=immutable`, every request profile time-bounded, and mutations never retried.
