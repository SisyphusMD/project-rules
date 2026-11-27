# #93 Describe the Forgejo release and publishing flow

- Kind: pull, state: closed, by cody, created 2026-11-17T13:46:03-08:00
- Labels: none; milestone: none
- refs/pull/93/head -> main, merged: True

Closes #91

The shared release helper comments still described macOS and arm64 builds on GitHub runners and omitted the NAS bottle refresh. They now describe how the Forgejo release feeds apt/dnf, the NAS bottle refresh, the install matrix and the independent PyPI and release publication checks.

No tests: comment-only edits to the shell helpers. The diff was checked for executable changes and all five revised scripts passed ShellCheck.


## forgejo-actions, 2026-11-17T13:46:31-08:00

<!-- ai-review -->
**AI review** of `42fbcb3c07`: Comment-only corrections across five shared release-helper scripts to replace stale GitHub/mirrored-tag wording with the current Forgejo workflow model, as requested by issue #91. All hunks are within `#` comment lines; no executable code is touched. The CHANGELOG entry and issue link are present, and the 'No tests' justification is valid for a comment-only change.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
