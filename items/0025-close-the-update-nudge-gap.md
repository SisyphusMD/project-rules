# #25 Close the update nudge gap

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:29-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#4 (pull request, opened by cody on 2026-08-23, merged 2026-08-23). Branch `refs/pull/4/head` into `main`._

The last entry in "Still open, and NOT justified" is closed: both projects pick the release endpoint by channel and keep one marker per channel.

Records why the two halves have to land together - the marker leak only becomes possible once the candidate endpoint exists - and the trap the port laid, where four tests spelled a channel-derived marker literally and would have failed the next rc cut.
