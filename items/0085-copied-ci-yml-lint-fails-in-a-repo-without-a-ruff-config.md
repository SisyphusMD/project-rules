# #85 Copied ci.yml Lint fails in a repo without a ruff config

- Kind: issue, state: open, by cody, created 2026-11-17T11:09:36-08:00
- Labels: status:ready, type:bug; milestone: none

`ci.yml`'s Lint job runs `ruff check .` in the consuming repo with that repo's config. With no ruff config, ruff 0.17.5's defaults flag the copied `.forgejo/scripts/*.py` (EXE001, FURB167, TRY004) and the vendored `packaging/check-doc-links.py` (FURB167), which this repo lints under its own `[tool.ruff]` selection. Found adopting appliance-job-monitor (#73): a clean venv with `ruff==0.17.5` fails 13 findings, all in copied or vendored files.

That repo works around it with a `ruff.toml` that excludes `.forgejo/scripts` and `packaging`. Options for the fix here: make the copied files clean under ruff's defaults (cheap: `re.MULTILINE`/`re.DOTALL`, `TypeError`, executable bit), or have Lint pass `--extend-exclude .forgejo/scripts,packaging`, or tell `docs/adopting.md` to add that exclude. whiskerless and dreame-valetudo hit the same when they adopt (#71, #72).
