# #47 vendor.py follows a symlinked parent of a destination

- Kind: issue, state: open, by cody, created 2026-11-16T14:17:55-08:00
- Labels: status:ready, type:bug; milestone: none

Found in the second-model review of the first commit. tools/vendor.py writes each vendored file under the consumer checkout, but only checks the final path, not its parents. If a consumer has a directory on the destination path that is a symlink (say packaging/ -> /somewhere), vendoring writes outside the checkout. Fix: resolve every destination and refuse unless it stays under the consumer root, with a test that plants a symlinked parent. Safety-critical code: 100% branch coverage.
