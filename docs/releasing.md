# Releasing from protected main

Stable releases use two maintainer dispatches. Prepare Release runs the repository's
existing qualification and opens a pull request from `release/vX.Y.Z` into `main`.
The branch carries the changelog promotion, version stamps and any other release
files that were qualified. The pull request closes a release issue and goes through
the usual checks and merge. Merge it up to date so its tree matches the candidate
that passed qualification.

When ready to publish, dispatch Publish Release from `main` with the merged
pull request number. The release job runs trusted code from `main` and fetches
the primary's current `main`, tag refs and the nominated pull request. The job
passes the API response to `packaging/verify-release-pr.py` with the repository,
pull request number and fetched main SHA. This checks the exact merge commit,
the candidate tree, the latest released changelog entry and the primary’s tag refs. Check any
repository-specific version stamp against the verified tree before tagging.

Create an annotated tag at the returned commit. Push it with
`packaging/push-tag.sh <tag> <token> --merged-commit <sha>` or the repository's
equivalent tag-only publisher. The push must never update `main` or replace an
existing tag. A retry with an existing annotated tag on the same commit can
continue using that tag. Serialize stable release publishes within each
repository. Keep write credentials scoped to that repository and present
only in the trusted publish job.

The tag triggers the existing artifact publishers. If an artifact job fails,
retry publishing from the same tag. Consumers such as the Homebrew tap must
use their own pull requests for changes to protected branches.

An existing release workflow can keep the branch-and-tag helper until it has
switched to these two dispatches. Confirm the new release flow and its checks
before blocking direct pushes to the repository's `main`.
