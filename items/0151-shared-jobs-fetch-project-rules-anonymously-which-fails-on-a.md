# #151 Shared jobs fetch project-rules anonymously, which fails on a git host that requires sign-in to view

- Kind: issue, state: closed, by cody, created 2026-11-27T11:31:47-08:00
- Labels: type:bug; milestone: none

The shared jobs fetch project-rules anonymously, which fails on a git host that requires sign-in to view.

Every "Fetch the gate scripts" step (gate.yml, gate-lint.yml, review.yml, archive.yml, and the copy tests.yml proves) runs `git clone $FORGEJO_URL/SisyphusMD/project-rules.git` with no credentials. On a Forgejo instance with `REQUIRE_SIGNIN_VIEW=true`, that clone fails with "could not read Username", so every required check and the nightly archive fail before they start. The same clone with the job token works.

Plan: give the step the job token and send it as an `http.extraHeader` on that one command, so it never lands in the clone URL, the log or `.git/config`. Hosts that allow anonymous reads keep working, since the token can read a public repo. The tests that hold every copy of the step equal cover the new copies too, including gate-lint.yml's.

## cody, 2026-11-27T12:03:45-08:00

Status 2026-11-27: done. #152 merged as 5c63dec; every "Fetch the gate scripts" step now clones with the job token, passed through `git --config-env` so it stays out of argv, the log and `.git/config`.

Proof after the merge:
- A normal PR run on another repo passed, and every gate job logged `gate scripts: project-rules 5c63dec12c9aa60b160ded29037f4f082818eef4` (Issue link, Tests with code, Diff size, Copies match, Lint, Secrets).
- A workflow_dispatch of "Issue archive" on another repo succeeded and pushed its issue-archive branch (d5d1a36 to 680dbf8), logging the same `gate scripts:` line.
- The pull mirror on the sign-in-required host shows the same main head (5c63dec).

Review: `cx review` saw the first version of the diff. Its two findings (the header in argv shows up in git's trace output; the file:// test never proved a server got the header) led to the `--config-env` change and a local `git http-backend` test that refuses an anonymous clone. That rework was covered by CI and the AI review only.

Next: nothing here. Whether the shared jobs actually run on the sign-in-required host is still blocked on that host's action resolution, which is tracked there.
