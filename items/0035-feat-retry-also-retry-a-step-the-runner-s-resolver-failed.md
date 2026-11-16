# #35 feat(retry): also retry a step the runner's resolver failed

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:32-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#17 (pull request, opened by cody on 2026-09-16, merged 2026-09-16). Branch `refs/pull/17/head` into `main`._

Observed on whiskerless run 35055059591: `brew test` bootstrapped Homebrew's Ruby harness and the macOS runner could not resolve rubygems.org. The failure landed in one of our named steps, so the step-name rule refused the retry and the run stayed red until Renovate pushed again.

The discriminator now also reads each failed job's log. A step of ours is retryable only when its closing lines, bounded to its own timestamps with boundary seconds excluded, carry an exact resolver-failure spelling AND name a host CI is known to reach. Tests pin the refusals: a log printed by another step, a resolver error the step survived, a typo'd hostname, timeouts and refusals, a missing log, and a genuine failure elsewhere in the run.

Consumers need `gh api --allow-escape-sequences .../jobs/<id>/logs` per failed job and to pass the logs directory; that lands with the pin bump in each.
