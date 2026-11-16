# Shell, packaging and workflows

For every project that ships releases or runs CI, on top of [code.md](code.md).

## 1. Shell, packaging, and workflows

Every item below is a scar. Treat them as settled.

- Operational Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, quote every expansion, validate
  targets explicitly, pass ShellCheck at `--severity=warning` under a **digest-pinned** image.
- **Bound every HTTP call.** An unreachable host otherwise hangs with no deadline and strands every
  step sequenced after it. Reads may retry; **mutations must not** — a timed-out write may already
  have applied, and repeating it duplicates rather than recovers.
- TLS verification is never disabled. `curl -k` with a credential attached is a credential handed to
  whoever is in the middle. There is no "it's my own server" exemption when the request crosses the
  public internet.
- Publication is **immutable**: same name, same bytes, forever. Identical bytes are an idempotent
  no-op; different bytes under an existing name are a hard failure needing a new tag. **Never delete
  an object to replace it** — that window is where a re-driven partial publish loses an artifact.
- A 2xx is the forge's word, not evidence. **Read back** every mutation and compare bytes.
- Look tags up with the **exact** endpoint. GitHub's plural `git/refs/tags/<tag>` is a *prefix*
  match: waiting for `v0.2.0` is satisfied by an existing `v0.2.0-rc.1`. Use singular `git/ref/`,
  and check the wait's result — an exhausted wait must fail closed, never fall through into creating
  a release that mints its own tag from the default branch.
- **GitHub rewrites `~` to `.` in stored asset names** and enforces uniqueness on the rewritten form;
  Forgejo stores names verbatim. Any project whose artifact filenames carry a native package version
  must normalise the name for lookup and upload while still comparing bytes against the local file.
- Coupled refs go up with `git push --atomic`, then get read back. Prefer
  `http.extraheader` over embedding a token in the remote URL.
- Build contexts are explicit allowlists. `.dockerignore` is defense in depth, not the boundary —
  `docker cp .` ignores it entirely. Keep signing material out of the build context and in a
  `mktemp` file with a cleanup trap, copied to its own path.
- Third-party actions are pinned to full commit SHAs with a readable version comment. **Keep the
  `# renovate:` marker beside every pin** — remove it and that pin silently stops being updated.
- Default workflow permissions read-only; write scope and secrets live on the consuming step only.
- Self-hosted and persistent runners execute **only trusted same-repository code**. Gate PR jobs on
  `github.event.pull_request.head.repo.full_name == github.repository`.
- CI runs the literal floor interpreter, a current one, static checks, tests, installed artifacts,
  and the declared platform matrix. Hand-maintained file lists get a discovery invariant so a new
  shipped file cannot silently escape lint or tests.

## 2. Renovate postUpgradeTask scripts

A script Renovate runs on the update branch executes **inside Renovate's own container**, not your
CI image. That container is Node-based and carries none of your toolchain.

- Write in pure shell by default, and assume no GNU-only utility flags. The image happens to ship
  a `python3` today, but that is an accident of how it is built, not a promise it makes: treat it
  as absent unless a script checks for it and fails closed with a message naming what is missing.
  A task that reaches for an interpreter it never verified fails on a future image rebuild with a
  bare `command not found`, on an update branch nobody is watching.
- Handle both checksum spellings: `sha256sum` on Linux runners, `shasum -a 256` on macOS.
- **Refuse to write a digest you could not fetch.** A pin invented after a failed download makes
  every later build verify against nothing. Note that a failed `curl` piped into a hasher still
  produces a *valid-looking* hash — the one for empty input — so the guard must be `pipefail` plus
  `set -e`, not a non-empty check on the result.
- **Read the pin back** after rewriting and fail if it did not take.

The converged siblings already do all of this. It is written down because it is the kind of knowledge that
lives in one repo's comments until the day someone writes a second script without it.

Deliberately **not** shared: the pin inventories themselves. Which pins exist and which files hold
them is genuinely project-specific — Whisk pins a CPython tarball checksum inside a workflow, Dreame
pins helper digests in `constants.py` and its Homebrew formulae. Factoring a fifteen-line helper out
from under those would buy nothing.

## 3. Artifact filenames carry the NATIVE package version

Every published artifact carries its version in the filename, so two downloads in `~/Downloads` can
be told apart and the second does not silently overwrite the first.

**The spelling is whatever the packaging system itself reports — not the git tag.** These differ,
and the difference is deliberate rather than an inconsistency to "fix":

| Artifact | Tag `v0.3.0-rc.17` becomes | Because |
|---|---|---|
| `.deb` / `.rpm` | `0.3.0~rc.17` | nfpm normalises a semver prerelease to the `~` form; `dpkg -I` and `rpm -qi` report that, and a file must be named after what it contains |
| `.pkg` | `0.3.0-rc.17` | `pkgbuild --version` stores the string verbatim, so the tag form *is* the native form |
| source tarball | `0.3.0-rc.17` | no packaging system normalises it |

Derive the package form once, next to where the tag is read, and use that variable for filenames:

```bash
export VERSION="${GITHUB_REF_NAME#v}"   # the tag form, for nfpm and pkgbuild --version
PKGVER="${VERSION/-rc./~rc.}"           # the native form, for .deb/.rpm FILENAMES
```

Two consequences that are easy to miss, and both have bitten:

- **GitHub rewrites `~` to `.` in the stored asset name** and enforces uniqueness on the rewritten
  form; Forgejo stores it verbatim. Two consequences, and the second is the one that bites:
  - Never construct a GitHub asset URL from the local filename — go through
    `rel_github_asset_name()` in `shared/packaging/release-common.sh`.
  - **Never compare asset names across registries literally.** One asset answers to two spellings,
    so a literal comparison reports one asset as two — which reads as "ambiguous", not as "equal",
    and makes tooling *refuse* rather than fail loudly. Collapse to the canonical (`~`→`.`) form to
    compare, and keep the verbatim spelling as the name to upload. This is silent by construction:
    the release still goes green while cross-registry self-healing quietly stops.
- **Nothing may match these names literally.** Reconcile matches by *role* glob, the release
  completeness gate matches by *suffix*, and the README is stamped only on a stable release. A
  literal name in any of those is a latent break the next time the scheme moves — and a rename
  applied to the build step but not to the test/upload/gate steps breaks the release outright.

## 4. A release gate must run on the RELEASE path

CI runs on a branch; a release is cut from a tag. A gate that lives only in `ci.yml` does not
constrain what a release may ship. Every non-regression gate — coverage, lint, type-check, the
version-of-record check — runs in `ci.yml` **and** in `release.yml` **and** in `prerelease.yml`.
