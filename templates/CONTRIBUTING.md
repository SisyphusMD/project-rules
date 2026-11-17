# Contributing

This repo follows the SisyphusMD project rules:
https://forgejo.bryantserver.com/SisyphusMD/project-rules/src/branch/main/RULES.md

Read them first. Issues and pull requests are opened on Forgejo, where you can sign in with GitHub.
A new account waits for a maintainer to activate it and cannot fork, so pull requests are sent with
AGit: `git push origin HEAD:refs/for/main -o topic=<short-name>` from a Forgejo clone. This file
adds only what is specific to this repo and never loosens the rules. Note rule 9 in particular:
no AI attribution, such as a `Co-Authored-By` trailer for an assistant, anywhere in a contribution.

## Tests

- **Run them**: `<command>`
- **What counts as a test here**: <for code that CI cannot run, say how it is tested and
  where the proof goes in the PR>
- **Safety-critical code** (100% coverage): <paths, or "none">

## Required checks

The standard set from the rules, plus: <this repo's own checks>.

## Break-glass

<What can be down that blocks a merge here, and the exact recovery steps.>
