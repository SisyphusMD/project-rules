# Python conventions

For every Python project, on top of [code.md](code.md).

## 1. Python, typing, and code shape

| Topic | Convention | Permitted variance |
|---|---|---|
| **Language floor** | One literal minimum Python version, stated identically in packaging metadata, type-check config, lint config, CI, and docs. CI executes that **exact patch release**, not just its minor series. | A framework-specific job may need a newer interpreter, but it never raises the base contract silently. |
| **Formatting** | UTF-8, LF, final newline, no trailing whitespace, spaces. Four-space Python, two-space everything else. 100-column Python lines. | Generated and vendored files keep their upstream format. Markdown tables may exceed 100 columns where wrapping would hurt readability. |
| **Linting** | A shared Ruff baseline with explicit `target-version`. A rule is disabled only for a concrete incompatibility, never to silence a backlog. | Domain overlays differ: `ASYNC` only where async exists; BLE, subprocess, and packaging overlays may add rules. |
| **Type checking** | Exact-pinned mypy with `strict = true` and `warn_unreachable = true`. Pin it, because `strict` semantics move between releases. Type the test fixtures that expose recording objects rather than scattering `type: ignore`. | Being typed does not make an internal module a supported public API. |
| **Value objects** | Frozen, slotted dataclasses for identities, parsed protocol values, and immutable results. Anything advertised as immutable defensively copies caller input and makes nested collections immutable enough to prevent alias mutation — otherwise call it a shallow view and name it that way. | Mutable orchestration objects are right when they explicitly own effects or evolving session state. |
| **Parsing** | Parse untrusted bytes, archives, and persisted state **once**, at a defensive boundary, into typed values. Preserve unknown/raw values — a future firmware will add them. Pure decisions consume typed values, not scattered strings or marker filenames. | Disk and wire encodings stay project-specific and backward-compatible. |
| **Effects** | Environment, console, clock, sleep, subprocess/device runner, and persistence sit behind an explicit context or narrow injectable seam. Pure validation, planning, and transition decisions stay separate from effects. | Async vs synchronous internals — for the siblings, see [VARIANCE.md](../VARIANCE.md). |
| **Errors** | Project-owned typed exceptions wherever callers or recovery behaviour differ; always `raise ... from exc`. Expected operational failures reach **one** CLI error funnel. Programmer faults stay visible under `--debug`. | A consumed library curates a public exception hierarchy; a CLI-only application may keep narrower internal types. |
| **Module size** | Split at stable semantic boundaries — parse/dispatch, persistence/migration, pure planning vs effects. Characterise behaviour with tests first. Line count is a signal, never a reason on its own. | Do not split an ordered flash sequence or a transport loop just to make two repos look symmetrical. |

## 2. Naming, imports, and public surfaces

Use domain names that distinguish concepts instead of reusing a convenient generic noun.

Rules:

- Keep stable public names compatible. A clearer name for a public symbol or CLI verb ships with a
  documented alias and deprecation window, plus an installed-artifact compatibility test.
- Prefer explicit project-package imports. No import-time I/O, no mutable module globals used to
  communicate between phases, no wildcard imports, no accidental re-export of internals.
- Public library exports are listed deliberately in `__all__`. Ship `py.typed` only alongside an
  explicit compatibility promise.
- `snake_case` functions, `PascalCase` types, `UPPER_SNAKE_CASE` constants. Predicates read as
  questions: `is_`, `has_`, `can_`, `supports_`.

## 3. CLI and UX

- A bare invocation or empty state gives the user the **next valid action**. It must never recommend
  a command whose own preconditions reject the pristine state.
- Prompts state effect, target, what is retained or deleted, reversibility, and recovery, in
  proportion to risk. Destructive identity-changing operations require typed, target-specific
  confirmation; ordinary optional actions use a plain yes/no.
- **Never map an unrecognised input to a silent default.** `set <thing> enabled` must not quietly
  mean *off* because `enabled` was not in the accepted list. Unknown booleans, invalid numbers, and
  malformed times produce a concise typed error or a bounded re-prompt — never silent false, never a
  traceback.
- Every parse that can raise reaches the CLI error funnel. A mistyped time is a one-line message,
  not a stack trace.
- EOF and interruption cancel with **zero** new effects.
- Success prints only after the promised postcondition is observed or durable state is read back.
  Warnings precede the affected action. Partial progress names the completed boundary and the exact
  resume instruction.
- All output flows through an injectable console. Non-TTY and `NO_COLOR` output stays ordered,
  bounded, and semantically complete — colour and spinners never carry the only status meaning.
- **Bound what you print by output, not by input count.** Capping "the newest 3 changelog sections"
  does not bound anything when one section is 166 lines.
- Every subcommand has its own `--help`. Global usage in response to `cmd sub --help` is a bug.
- Error messages lead with the actionable problem, name the target safely, and give one concrete
  remedy. `--debug` adds the traceback with a privacy warning.

## 4. Lint codes in shared files

A vendored file carries **no `# noqa` directives naming a project's rule codes.** Consumers do not
enable the same rule set, so a code one of them does not select reads as an unused directive
in that repo and fails `RUF100` — the suppression itself becomes the lint error.

Instead, the consumer whose rule set objects adds a `per-file-ignores` entry naming the vendored
path. The exemption belongs with the configuration that created the need for it.

Measured on the siblings: converging Whiskerless onto Dreame's rule set costs 12 `PLC0415`
findings in production code (deliberate lazy imports for optional heavy dependencies — keep them
ignored, they are an architectural choice, not a backlog) and **5 `PLW0603` findings, all of them
the migration globals in `profiles.py`.** That second one is worth having: it is a real design
defect that a converged lint config would have surfaced automatically.
