# The converged siblings

`whiskerless` and `dreame-valetudo` deliberately share a release pipeline, packaging layout, CI
split, Renovate policy and the vendored `shared/` tree. They differ only where
[VARIANCE.md](../VARIANCE.md) says so; anything not recorded there is drift.

## Shared vocabulary

- **`DeviceProfile`** — static supported-device capabilities.
- **`RobotRecord`** / **`SavedRobot`** — a mutable persisted installation record.
- **`RobotIdentity`** — serial, model, or config value used to verify the physical robot.
- **`State`** / **`Snapshot`** — a typed observation at a point in time, never an on-disk profile.
- **`Plan`** / **`Decision`** / **`Transition`** — pure output describing effects without performing them.

## The sibling rule

Every improvement to one project is evaluated for the other. Not "considered eventually" — evaluated
in the same change, with one of four outcomes: **ported**, **ported with a project-specific
implementation**, **not applicable** (say why), or **deliberate variance** (record it in
`VARIANCE.md`).

The enforcement is one line in the pull request template:

> ☐ Sibling repo: ported / not applicable because …

"Not noticed" and "different project" are not answers. This costs a sentence per PR, which is why it
will actually happen — and it is the single rule that, had it existed, would have prevented most of
what the convergence audit found.
