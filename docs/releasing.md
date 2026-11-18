# Releasing from protected main

Stable releases use two maintainer dispatches. Prepare Release runs the repository's
existing qualification and opens a pull request from `release/vX.Y.Z` into `main`.
The branch carries the changelog promotion, version stamps and any other release
files that were qualified. The pull request closes a release issue and goes through
the usual checks and merge. Merge it up to date so its tree matches the candidate
that passed qualification.

Record the candidate's full commit SHA after qualification. The trusted Prepare
Release job that opens the PR writes `Qualified release commit: <sha>` to its log
and posts a successful `Release / Qualified candidate` status on that SHA with
the workflow run URL. Use the verified candidate only. The job that records
it and pushes its branch runs independently of candidate-supplied code.

When ready to publish, dispatch Publish Release from `main` with the merged
pull request number. The release job runs trusted code from `main` and fetches
the primary's current `main`, tag refs and the nominated pull request. The job
passes the API response to `packaging/verify-release-pr.py` with the repository,
pull request number and fetched main SHA. This checks the exact merge commit,
the candidate tree, the latest released changelog entry and the primary’s tag refs. Check any
repository-specific version stamp against the verified tree before tagging.

Before creating a tag, fetch the PR head commit and run
`python3 -I packaging/verify-release-qualification.py` with the head SHA, the
Prepare Release workflow filename and the name of its recording job. Supply
`FORGEJO_READ_TOKEN` for the primary's commit status, run and job APIs.
Use the primary's public Forgejo URL in `GITHUB_SERVER_URL` so the recorded URL
and the one from the run API identify the same run.
The helper checks the successful main dispatch's base commit and its record of
the exact candidate. If the prepared head changes, qualify a new candidate.
Projects that prepare on a licensed local toolchain or on a maintenance channel
may supply equivalent exact-candidate evidence in their publish verifier.

Create an annotated tag at the returned commit. Push it with
`packaging/push-tag.sh <tag> <token> --merged-commit <sha>` or the repository's
equivalent tag-only publisher. The push must never update `main` or replace an
existing tag. A retry with an existing annotated tag on the same commit can
continue using that tag after checking its exact ref and target. Serialize stable
release publishes within each repository. Keep write credentials scoped to it and present
only in the trusted publish job.

The tag triggers the existing artifact publishers. If an artifact job fails,
retry publishing from the same tag. Consumers such as the Homebrew tap must
use their own pull requests for changes to protected branches.

An existing release workflow can keep the branch-and-tag helper until it has
switched to these two dispatches. Confirm the new release flow and its checks
before blocking direct pushes to the repository's `main`.
