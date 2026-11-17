# #49 check-mirror-ci.sh calls curl with no timeout

- Kind: issue, state: closed, by cody, created 2026-11-16T14:17:56-08:00
- Labels: status:ready, type:bug; milestone: none

Found in the second-model review of the first commit. shared/packaging/check-mirror-ci.sh runs curl without --max-time or --connect-timeout, so a hung mirror host stalls the release job until the runner's job timeout. Fix: bounded timeouts and a retry, failing closed, with a test that points it at a port that never answers.

## cody, 2026-11-16T18:25:28-08:00

Obsolete: #53 (merged, 6d37364) deleted check-mirror-ci.sh with the GitHub-runner helpers; its replacement check-forgejo-ci.sh is new code with its own tests.
