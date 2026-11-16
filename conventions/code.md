# Code, tests and documentation

Language-independent conventions for every project. Each one exists because breaking it
already cost something. The process rules are in [RULES.md](../RULES.md).

## 1. Comments

Comment the non-obvious **why** — the invariant, the constraint, the consequence, the recovery
requirement. Never narrate what the code plainly does.

- Earn every line. Tighten verbose comments; never strip load-bearing *why* just because it is long.
- No changelog or war stories: not "was N of M", not "the old regex…", not "added for issue #12".
  That belongs in the commit message. Historical reasoning that must survive goes in a dated note,
  linked from a short current-invariant comment.
- No cryptic labels without context ("Option C:").
- **A comment that contradicts the code, or another comment in the same file, is a defect.** Both
  repos have shipped these. Examples found and fixed: a docstring pointing at a function that does
  not exist; a module docstring declaring "one secret lives here" three lines above "two kinds of
  secret live here"; a Windows accommodation asserting "the store holds no secrets" in a file whose
  own docstring lists the CA private key.
- Leave vendored and upstream-copied boilerplate as-is. Do not tidy it into divergence.

## 2. DRY, and what "shared" means

1. Remove duplication when two paths share the same **invariant and failure semantics** — not merely
   similar-looking code.
2. Keep product protocols, state machines, hardware sequences, retry timing, and framework adapters
   project-local. Do not force MQTT register writes and Home Assistant state writes into one helper
   when their verification and pacing differ.
3. Genuinely shared, project-agnostic code lives in **`SisyphusMD/project-rules`** (`shared/`) and
   is **vendored** — physically committed — into each consumer, with `STANDARD.lock` recording the
   source tag and per-file SHA-256.
4. **No submodule, no runtime fetch, no cross-repo package.** An old tag must still build and release
   offline, years later, with the standard repository unreachable. This constraint is not negotiable;
   it is the only reason a shared standard is safe.
5. Never improve a shared helper by editing the vendored copy. Change it here, re-vendor
   **every** consumer, land them together. `tools/check.py` fails CI when a copy is edited in place —
   that is the mechanism, and editing around it defeats the entire arrangement.
6. `packaging/project.env` holds each project's parameters and is deliberately outside the lock.

## 3. Tests

| Layer | Convention |
|---|---|
| **Pure unit** | Table-test parsers, codecs, reducers, preconditions, migration decisions, and version ordering with no real effects. Prove unknown values round-trip and that caller-owned input cannot mutate a snapshot. |
| **Effect seam** | Recording runners, scripted consoles, fake clocks, fake MQTT/BLE links, controlled filesystems. Assert **exact** argv, transcript, wire bytes, call order — and **zero calls** on denial. |
| **Public behaviour** | Exercise the real entry point: exit code, stdout/stderr, cancellation, `--debug`, and what state is retained versus deleted. Avoid tests coupled only to private details. |
| **Installed artifact** | Build the real wheel/package/bottle, install into a clean environment, run its declared entry points, then remove or upgrade it. Imports must not rely on the checkout being importable — that masks packaging failures. |
| **Published artifact** | Download from **every** promised origin and bind to the expected digest. One forge is never evidence for another. |
| **Physical hardware** | Record artifact digest, device model, firmware, scenario, and outcome. Evidence is for those exact bytes on that exact firmware — not for a differently-stamped rebuild. |

- Name tests for observable behaviour: `test_restore_rejects_duplicate_canonical_path_before_write`.
- Every bug fix carries the lowest practical regression that **fails on the parent commit**.
- Destructive-path denials assert exact negative postconditions, not just an error message.
- Randomness and time are injected or seeded. Network and hardware access are opt-in, named suites —
  an ordinary unit run never discovers and touches a live device.
- Coverage is branch-aware: **99%** overall and **100%** on the safety-critical code a repo's
  `CONTRIBUTING.md` names (final mutation guards, destructive preflight, error funnels, runner
  seams). See rule 13.

## 4. A check that cannot be shown to fail is not evidence

Every convergence probe, invariant test and drift gate is run against a state where it MUST fail,
before it is trusted. Not as a nicety — four separate checks in the converged siblings passed while measuring
nothing:

- a probe matching `workflows/ci-pr.yml` in *file contents*, which matched the sentence in
  `CONTRIBUTING.md` describing the workflow, and reported both projects as having it while one had
  no such file;
- a probe matching `DEBIAN_FLOOR_IMAGE`, reporting install-matrix parity across a 44-stage-versus-
  5-stage difference;
- a test asserting the bundled consumer imports nothing unpromised, whose off-by-one in a module
  path split made it pass while two submodules leaked;
- a test asserting `pytest.raises(Die)` on an abort path, where the exit-0 subclass and the exit-1
  base both satisfy it, so the exit code it existed to pin was never checked.

Each looked like coverage and was decoration. The negative control is the cheap part: point the
check at the repository before the change, or delete the export it depends on, and watch it go red.
If it does not, the check is measuring a mention, a substring, or a superclass — not the thing.

**Corollary: prefer file existence or a call site to a substring.** "Does this word appear
somewhere" is the failure mode; "does this file exist" and "is this function actually called with
these arguments" cannot be satisfied by prose describing them.

## 5. State the licence, and why it follows from who consumes you

Every project records its licence **and the reasoning** in `CONTRIBUTING.md`. Not the licence name —
the argument. Three questions, answered in order:

1. **Who consumes this?** Nobody (a standalone tool), other code (a library), or a network service.
2. **What does that make copyleft cost?** For a standalone tool, nothing. For a library imported
   into someone else's application, it reaches their combined work. For anything network-served,
   AGPL's section 13 reaches users who were never handed a copy.
3. **What does the ecosystem around it use?** A licence out of step with its neighbours is friction
   with no benefit, and can foreclose futures — an upstream that refuses copyleft dependencies is a
   door that closes on day one.

The two converged siblings answer differently and both are right: whiskerless is MIT because
Home Assistant imports it; dreame-valetudo is GPL-3.0 because nothing imports it. **A licence
difference between sibling projects is not drift** — but an *undocumented* one is, because the next
person cannot tell which it was.

Also record what third-party code ships alongside, and whether it is **linked** or merely
**executed**. Executing a GPL-2.0 binary as a separate process is aggregation and imposes nothing;
linking it is a combined work. That distinction decides whether a bundled helper is a non-issue or a
licence violation, and it is invisible from the file list.

## 6. Name the surface you promise, and let a consumer prove it

Every project states, in `CONTRIBUTING.md`, exactly what it will not break — and everything not
named is explicitly free to change. Without that, every symbol is potentially load-bearing and
nothing can be refactored with confidence.

**The surface differs by who consumes you; the discipline does not.** A library that other code
imports promises names and types. An application nobody imports promises its CLI: subcommand names,
flags, exit codes, and any on-disk layout holding data a user cannot recreate. Both promise exit
codes, because both get scripted. Neither promises human-readable output text — a caller parsing
prose is depending on something that was never offered.

**Do not promise output text, and say so.** It is the difference between being able to improve a
message and being stuck with a typo forever.

**Enforce the promise against a real consumer, not against good intentions.** The failure mode is
not someone breaking a promised name — that gets caught. It is the promise staying small and true
while the actual consumed surface grows around it, so a rename that every check called safe breaks
a consumer the promise said did not exist. If you ship a consumer (a bundled integration, an
example, a smoke test), make a test assert that everything it imports is inside the promise. When
that test fails, the honest fixes are to widen the promise or make the consumer need less —
never to quietly keep reaching past it.

Changing a promised name means keeping the old spelling working, recording the deprecation in
`CHANGELOG.md`, and removing it no sooner than the next MINOR release. Additions need no window.

## 7. Documentation, changelog, repository

- PEP 621 + Hatchling, `README.md`, `CHANGELOG.md`, SPDX license metadata, `LICENSE`, contribution
  guidance, security/support routing, machine-readable project URLs.
- Changelogs explicitly follow Keep a Changelog and SemVer and retain one `Unreleased` section.
- Documentation is journey-first: prerequisites, support status, install, first run, normal
  operation, update, candidate opt-in and return, backup and recovery, uninstall, troubleshooting.
  **Commands shown in a journey must be executable in that order on a clean system.**
- Generated facts have one source. Command names, channels, versions, package filenames, and support
  tiers render from manifests and are checked for drift. Do not duplicate a numeric threshold in
  prose when CI is authoritative.
- Recovery and uninstall text states exactly what is retained, deleted, reversible, and
  device-affecting.
- **Version-relative statements must say which version they are relative to.** "Returning to stable
  is a downgrade" is true while the candidate is ahead of the published stable and false afterwards.
  Write the condition, not just the conclusion.
- Ignore files are a safe union of virtual environments, build outputs, packages, signing material,
  platform metadata, and local tool state. They are not a security control.

## 8. Documentation names the thing; it does not speak as "we"

Reference documentation is written in the third person. **Second person stays** — telling a reader
what *you* do is ordinary technical writing, and rewriting it into passive voice makes instructions
worse. This is about the first person only: "we", "our", "us".

The reason is not style. "our key" tells a reader nothing they can act on and quietly assumes they
know who "we" are; "the SisyphusMD signing key" names the thing, and a reader can go and look at it.

Two exceptions, both real:

- **Quoted program output stays verbatim.** A menu that reads `I already have one — I will give you
  the files` is the program speaking, and paraphrasing it in the docs means the docs no longer match
  the screen.
- **Some plurals are load-bearing.** Where a passage exists to distinguish *this* project's key
  from a third party's, deleting the possessive deletes the distinction. Rewrite to name both
  parties rather than to satisfy a grep — and never at the cost of epistemics: "on the unit we
  tested" becomes "on the one unit tested", which still says one unit, not "on tested units".
