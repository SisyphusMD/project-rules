# #107 AI review parser can accept a leaked reasoning draft as the verdict

- Kind: issue, state: open, by cody, created 2026-11-19T13:43:26-08:00
- Labels: status:ready, type:bug; milestone: none

Found by a Codex review of the cody/macos copy of #105's script (699f6bd). parse_answer falls back to the text after each </think>; when leaked reasoning contains braces, then a quoted </think>, then a schema-valid draft, and no final verdict follows, the suffix fallback can accept the draft. A draft with no findings would post success, so the gate would not fail closed (RULES.md fail-closed requirement). The pre-#105 parser rejected this shape. Next: require a reliable boundary before accepting a suffix and add a regression test for draft-only output.
