# #123 Canonical diff-size and tests-with-code are weaker than the several private repos copies

- Kind: issue, state: closed, by cody, created 2026-11-24T17:32:47-08:00
- Labels: status:in-progress, type:bug; milestone: none

`a private repo` and `a private repo` carry stricter copies of two gate scripts than this repo does, byte-identical to each other:

- `diff-size.py`: canonical runs `git diff --numstat` in the PR's checkout, so a `.gitattributes` in the PR that marks paths binary makes them count 0 lines. Their copy reads attributes from the base tree only and passes `--no-textconv --no-ext-diff`.
- `tests-with-code.py`: canonical counts code by extension only. Their copy also counts tracked executables (mode 100755) and `.zsh`, and reads paths NUL-separated, so a non-ASCII path is not skipped by its quoting.

Every repo will run canonical from main (#78), so without this those two repos' checks get weaker. The `diff-size.py` half is the `.gitattributes` part of #87 for that script; #87's Lint and Secrets halves stay there.

Found in the #78 inventory on 2026-11-24.

## cody, 2026-11-24T17:41:27-08:00

Landed in #124 (a05b905d). Consumers get it when they switch to running the scripts from main (#78); the two repos that already had a stricter copy keep theirs until then.
