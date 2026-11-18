# #101 Allow direct sync commits in the private memory repository

- Kind: issue, state: closed, by cody, created 2026-11-17T22:48:20-08:00
- Labels: status:in-progress, type:decision; milestone: none

Automatically synchronized agent memory notes need to reach other machines as ordinary versioned file updates. The maintainer approved a single private, memory-only repository for this purpose. Record an exception to rules 1, 6, and 19 for its repository-scoped sync identity. The exception covers automatic commits of memory notes and their indexes. Tools, scripts, hooks, configuration, and instructions keep the usual issue and pull request process.

## cody, 2026-11-17T22:48:32-08:00

Decision: One designated private repository for automatic memory notes and indexes may receive direct sync commits on main. Tools, scripts, hooks, shared settings, and instructions still go through issues and pull requests. Why: Shared memories can stay versioned and reach other machines automatically while changes to agent behavior follow the normal review process.

Decided by: Cody, 2026-11-17.

## cody, 2026-11-17T22:48:32-08:00

Taking the exception row, changelog entry, and required validation.
