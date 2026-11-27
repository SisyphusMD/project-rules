# #142 Keep private repo names and internal hosts out of public text and tracked files

- Kind: issue, state: open, by cody, created 2026-11-26T18:51:44-08:00
- Labels: none; milestone: none

Trigger: on 2026-11-26 private repository names and internal hostnames were found in this repo's public issue and PR text and in the nightly `issue-archive` branch, which push-mirrors to GitHub. The text was redacted and the archive branch rebuilt as a single commit (approved by Cody that day). Two follow-ups remain.

## 1. House hostnames in tracked files

Tracked files on main still name house-internal hosts: the release tooling under `shared/packaging/` hardcodes the house mirror host in its scripts. Move them to the owner manifest (or an argument) as #136 does for the gate workflows, so a public checkout names no internal host. The gate-lint and review.yml values are covered by #136; this issue is only the `shared/packaging/` scripts and anything else a grep for the house internal domains finds on main after #136 merges.

## 2. A check that keeps private names out of public issue text

A scheduled or event-driven job in this repo that, for every public repo it covers, reads issue, PR and comment text and fails or opens a single report issue when it finds a private repository name or an internal hostname. The list of private names comes from a source that is itself not public (a token-scoped repo search at run time, not a list committed here). Include editing history, since Forgejo shows prior revisions of an edited body or comment, and note that a changed title leaves a "changed title" timeline entry showing the old title that no API can remove. The check should therefore run on create and edit events where possible, so a leak is caught before it is mirrored.

Open: where the check runs (this repo's Tests workflow only covers this repo; other public repos copy the workflows), and whether a pre-mirror hold on the `issue-archive` branch is wanted as well.

## cody, 2026-11-26T20:22:38-08:00

Status 2026-11-26: the seven "changed title" timeline entries left by the redaction (Forgejo API delete was a no-op for that comment type) were deleted directly in the database with Cody's yes, after a row backup kept locally. No remaining title-change entry in this repo names a private repo; the issue pages no longer show them. The guard this issue asks for should cover title-change entries too.

## cody, 2026-11-26T22:13:39-08:00

Found 2026-11-26: public repos' Actions job logs are anonymously readable, and the runner's own lines (actions/checkout origin and extraheader setup, the runner image mirror, the host actions are fetched from) print internal hostnames in every job. The gate's own output carried no manifest value or private repo name. Fix belongs here: either the runner config stops printing internal names in public repos' jobs (public URL for checkout and actions), or public repos' logs stop being anonymous. Existing logs need pruning once fixed.
