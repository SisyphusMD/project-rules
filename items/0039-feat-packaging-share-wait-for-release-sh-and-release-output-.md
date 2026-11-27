# #39 feat(packaging): share wait-for-release.sh and release-output gitignore entries

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:34-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#30 (pull request, opened by cody on 2026-10-26, merged 2026-10-26). Branch `refs/pull/30/head` into `main`._

Both consumers had their own wait-for-release.sh and they had drifted: dreame treated the tap as ready on a `bottle do` block plus a version substring, never comparing bottle sha256s to the release manifests; whiskerless hardcoded its names and had a garbled section.

This is one project-agnostic script (union of both checks), parameterised from project.env (`PROJECT_REPO_SLUG`, new `PROJECT_TAP_SLUG`) and a per-repo `asset-roles.sh` data file. `fetch()` is confined to `$FORGE` and follows no redirects. Also: release-output entries in gitignore.base, VARIANCE contribution-routing line corrected (dreame has ci-pr.yml).
