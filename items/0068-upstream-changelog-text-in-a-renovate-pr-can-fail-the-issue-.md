# #68 Upstream changelog text in a Renovate PR can fail the issue-link check

- Kind: issue, state: open, by cody, created 2026-11-17T07:33:14-08:00
- Labels: status:ready, type:bug; milestone: none

Renovate puts upstream release notes in the PR body (fetchChangeLogs: pr). A line there such as 'fix #123' or 'refs #45' matches issue-link.py's pattern with no owner/repo, so it resolves against this repo and fails the check (or names an unrelated issue), and ai-review.py re-reads the same refs. Found reviewing #64; it applies to every repo running the gate with Renovate.

## cody, 2026-11-17T13:50:48-08:00

Adoption adds a Renovate footer with Refs and a standing local issue. Appliance-job-monitor PR #10 showed the AI review can block that form under rule 6 even after the issue-link job accepts it. Before requiring the gates on Renovate-managed repositories, verify against a real generated dependency PR that both checks accept the standing issue and ignore unrelated references in upstream release notes.

## cody, 2026-11-17T18:10:38-08:00

Live generated Dreame #300 and Whiskerless #220 passed Issue link and AI review with their Refs standing-issue footers. The included upstream v0.3.1 compare text did not contain bare issue numbers, so the unrelated changelog-reference case still needs its own regression proof. Both PRs hit a separate legacy release assertion, tracked in their release conversion issues.
