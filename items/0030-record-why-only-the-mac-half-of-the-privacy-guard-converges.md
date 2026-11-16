# #30 Record why only the MAC half of the privacy guard converges

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:31-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#10 (pull request, opened by cody on 2026-08-28, closed 2026-08-29). Branch `refs/pull/10/head` into `main`._

Both repos now gate their tree against committed hardware addresses with the same matcher. whiskerless additionally gates serials and dreame-valetudo does not — recorded here so a future convergence pass does not read it as accidental drift.

An LR4 serial has a fixed shape and doubles as the MQTT client-id and both topic segments. A Dreame serial is [A-Za-z0-9][A-Za-z0-9._-]{5,63}, so the same guard would match ordinary prose on every run, and a test that always fails is a test somebody deletes.
