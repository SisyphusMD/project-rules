# #29 Wait 90 minutes for the tap, not 30

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:30-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#8 (pull request, opened by cody on 2026-08-25, merged 2026-08-25). Branch `refs/pull/8/head` into `main`._

`build-bottles.sh` waits for publish.yml first tap pass; publish second pass then waits for the bottles built here. That handshake is correct. The BUDGET was not: 90 x 20s = 30 minutes, against a publish measured at 37m18s. The tap appeared 60 seconds after the loop gave up, and a release lost its bottles and the install matrix that waits on them.

Now 270 x 20s = 90 minutes. Widening is close to free: the loop breaks the moment the formula appears, so this is a FAILURE bound rather than a delay.

This applies to stable as much as to candidates - bottles.yml triggers on v*.*.* - and stable publish does more before the tap pass while a stable tag is permanent.

Both consumers gain a repo-local invariant failing under a 60-minute budget, mutation-tested against fewer iterations AND a shorter sleep.
