# #124 fix(gate): read attributes from the base only and count executables as code

- Kind: pull, state: closed, by cody, created 2026-11-24T17:36:19-08:00
- Labels: none; milestone: none
- refs/pull/124/head -> main, merged: True

Closes #123

A PR could add a `.gitattributes` marking its own files binary and `Diff size` counted them as 0 lines. `Diff size` now reads attributes from the base commit only and ignores user and system attribute files.

`Tests with code` counted code by extension, from the changed paths as git quotes them, so an extensionless executable, a `.zsh` file or a path git quotes (`café.py`) needed no test. It now counts tracked executables by their old or new mode (removing the bit in the same change does not exempt it), counts `.zsh`, includes type changes such as a symlink replaced by a script, and reads raw NUL-separated paths.

The first version of both came from `a private repo` and `a private repo`, which already run stricter copies; the old-mode, type-change and attribute-file parts are new here. The new tests in `tests/test_diff_size.py` and `tests/test_tests_with_code.py` reject each bypass above: all eight bypass tests fail against main's scripts.


## forgejo-actions, 2026-11-24T17:40:02-08:00

<!-- ai-review -->
**AI review** of `1379b54f2d`: The PR correctly strengthens both gate scripts as described in #123: diff-size.py now reads .gitattributes from the base tree only (via a temp worktree with GIT_ATTR_NOSYSTEM and core.attributesFile=/dev/null), and tests-with-code.py counts tracked executables, .zsh files, type changes, and reads NUL-separated paths. The eight new bypass tests cover each described attack, and the parsing of git diff --raw -z and --numstat -z output is correct for all status letters (A, C, M, R, T) including rename/copy two-path records.

No findings.

Disagree? Reply on this PR with your reasoning; the reviewer re-reads every reply.
<!-- ai-review-state W10= -->
