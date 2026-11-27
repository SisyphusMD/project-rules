# #78 Copied gate files are outside the drift lock

- Kind: issue, state: open, by cody, created 2026-11-17T08:41:25-08:00
- Labels: status:in-progress, type:feature; milestone: none

tools/vendor.py and STANDARD.lock cover shared/ only. The gate workflows, .forgejo/scripts, issue templates and .forgejo/RULES.md that each consumer copies (docs/adopting.md) carry no source tag and no drift check, so an in-place edit in a consumer is invisible and nobody can tell which version a copy came from. Extend vendoring to them so adoption and re-sync are mechanical. Found adopting appliance-job-monitor (#73).

## cody, 2026-11-17T12:30:34-08:00

Also: `.github/workflows/mirror-lockdown.yml` (#89) lacks the `# Canonical copy: SisyphusMD/project-rules; repos get a copy.` header the other copied workflows carry, so a consumer's copy doesn't say where it comes from. Add it when this drift lock lands (a header change means every consumer re-copies).

## cody, 2026-11-24T17:29:13-08:00

Decision: the gate-file drift issue becomes the shared version: every repo calls the gate scripts from project-rules main instead of keeping its own copy (asked "Should the gate-file drift issue become the shared version, with every repo calling the review scripts from project-rules main?", Cody: "Sure", after asking "shouldn't these things share code somewhere to avoid drift?"). Why: one copy cannot drift; accepted tradeoff: a bad merge in project-rules breaks every repo's review at once.

Decided by: Cody, 2026-11-24.

## cody, 2026-11-24T17:29:14-08:00

Owner: session "Shared review gate scripts" (the one that did the 72f8fcc rollout under #113). Starting with an inventory of what each repo's copy differs in, then the design here before any PR.

## cody, 2026-11-24T17:32:48-08:00

Inventory (2026-11-24), 15 other repos with the gate: ai-review.py is identical everywhere. diff-size.py and tests-with-code.py differ in several private repos (stricter there). ai-review.yml differs in six repos (no commenter gate), ci.yml in three, RULES.md in nine.

Technical call: each job clones project-rules main over HTTPS into a temp directory outside the PR checkout, logs the commit, runs the script with python3 -I and fails when the clone fails, with no local fallback. Job and workflow names stay as they are so the required contexts still match. Why not a `uses:` action: bare action names resolve to the mirror, and Renovate or the runner's action cache could hold it behind main.

Technical call: project-rules main then runs with every repo's job token and ISSUE_READ_TOKEN, so it is as sensitive as any of them; its protected main and required review are the guard.

Order: bring canonical up to the stricter copies (own issue), prove the clone on a runner, switch project-rules, pilot one repo with a passing and a failing PR, then the rest. The workflow YAML and RULES.md drift are not solved by sharing the scripts and stay open here.

## cody, 2026-11-24T17:51:52-08:00

project-rules now runs its gate scripts from main: #124 (stricter scripts), #125 (the fetch), #126 (lockdown header). Proof on #126 (head 41dd6447): `Issue link` logged `gate scripts: project-rules c869c2c9` and failed on the missing issue, then passed once the description named one. Next: SisyphusMD/homebrew-tap as the pilot, then the other repos, keeping a private repo' and a private repo's own Lint and Secrets steps.

## cody, 2026-11-24T18:24:07-08:00

Pilot done: SisyphusMD/homebrew-tap (#28 there, 27caff80), proven both ways on its #30. The other 14 repos wait on the maintainer's answer about whether the review also reads RULES.md from project-rules main, so each repo is touched once.

## cody, 2026-11-24T18:24:13-08:00

Correction to the counts above: 14 repos other than this one carry the gate, not 15, so 13 remain after the pilot: GhostSpectator, appliance-job-monitor, archiver, dreame-valetudo, whiskerless, several private repos, and bryantserver several private repos.

## cody, 2026-11-24T19:00:58-08:00

Decision: the AI review reads RULES.md from project-rules main, and repos stop carrying .forgejo/RULES.md (changes rule 22); the remaining 13 repos switch (asked "should the AI review also read RULES.md from project-rules main, so repos stop carrying their own copy?", with the 13 repos waiting on it; Cody: "Yes to all"). Why: 9 of 14 copies were out of date, so reviews there used old rules; accepted tradeoff: a rule change reaches every repo's reviews as soon as it merges.

Decided by: Cody, 2026-11-24.

## cody, 2026-11-24T19:41:50-08:00

Status: 13 of the 14 other repos with the gate now run the scripts and rules from project-rules main (all but a private repo, whose change is ready and waits behind that repo's 0.113.2 release). several private repos differ on purpose: no ISSUE_READ_TOKEN, and their own Lint and Secrets jobs. Proven live on project-rules and homebrew-tap. Not yet proven: a private repo judging a PR with the fetched scripts, and a real failed download (tests only). Workflow YAML is still a copy in each repo, so this issue stays open for that drift.

## cody, 2026-11-24T20:55:22-08:00

Correction and status: all 14 other repos with the gate now run the scripts and rules from project-rules main; a private repo was the last (a private repo, e3d4d6d2).

Not mentioned earlier: the private repos had kept the older ai-review.yml comment trigger on purpose (#116: outside accounts cannot see them, recorded on #113). several private repos now have the canonical one, where a comment re-runs the review only when the commenter can push or wrote the PR. The switch PRs say so, but the earlier decision was not weighed when they were written.

Proven live in private repos since then: a private repo run 46591 failed Issue link on a PR naming no issue, a private repo run 46512's AI review failed on a blocking finding, and the same jobs passed on other PRs, all at 6a6d41b4. A real failed download is still covered by tests only.

Still open: each repo carries a copy of the workflow YAML.

## cody, 2026-11-24T22:08:18-08:00

Private-repo proof both ways on one PR: a private repo PR #43's Issue link failed (run 46591) and passed once its description named an issue, both on scripts fetched from project-rules main. Next here: decide whether the workflow YAML should also stop being a copy in each repo.

## cody, 2026-11-24T22:10:18-08:00

Technical call: Private repos use the same AI review comment trigger as public ones (re-run only for someone who can push or the PR author), reversing the private-repo exception noted on #116 and #113. Why: One workflow file everywhere is what stops drift, and the exception existed only because outsiders cannot see private repos. The a private repo still triggers re-runs: a private repo had this rule when its main ran the babysitter's replies (runs 46343 and 46354), and it has the same write access in several private repos.

Decided by: Claude, 2026-11-24.

## cody, 2026-11-25T14:30:04-08:00

Decision: Finish this here: first test whether every repo can call one shared workflow in project-rules while keeping its required check names; if not, a scheduled job in project-rules compares each repo's workflow copies and opens a PR where one differs. Why: Each repo still carries copies of the gate workflows, which can drift (Cody: "yes" 2026-11-25, to sharing first with the scheduled check as the fallback).

Decided by: Cody, 2026-11-25.

## cody, 2026-11-25T14:30:05-08:00

Claude has this (session "Shared review gate scripts").

## cody, 2026-11-25T15:42:41-08:00

Shared workflows landed in #129 (d197413f): gate.yml, gate-lint.yml and review.yml, called by nothing yet. Probes on 17.0.2 (throwaway repo cody/gate-call-test): called jobs keep their check names plus one extra caller check; github.event_name reads workflow_call; named secrets pass, workflow_call may not declare them; concurrency in a called file is ignored; only public repos can be called; a missing ref or broken file fails the caller visibly. Fork PRs: checkout v7.0.1 keys its fork refusal on the event name, so the four head-checkout jobs apply the same rule themselves. Next: a pilot repo switches to callers and is proven failing and passing.

## cody, 2026-11-25T21:19:59-08:00

Pilot proven in homebrew-tap (#34, proof PR #35): a failure and a pass on the called jobs with unchanged check names, and a reply re-running the review. Next: project-rules' own ci.yml and ai-review.yml become the canonical callers, then the other repos switch.

## cody, 2026-11-25T22:21:35-08:00

Done. Every house repo's ci.yml and ai-review.yml now call gate.yml, gate-lint.yml and review.yml from main (#129 added them, #130 made this repo's own files the canonical callers, #131 fixed the header reference). Merged and verified: homebrew-tap (pilot plus proof PR), GhostSpectator, appliance-job-monitor, dreame-valetudo, whiskerless, archiver, several private repos. The 12 plain copies are byte-equal to main's callers; several private repos keep their own Lint and Secrets jobs beside the gate call, as adopting.md now allows.

What drift is left: each repo still copies a caller of about twenty lines (triggers, concurrency, the secret mapping), which a called workflow cannot hold. issue-archive.yml stays copied, since it pushes the repo's own archive branch, and mirror-lockdown.yml runs on GitHub, which cannot call a Forgejo workflow; both are out of scope here. The open question whether this repo should require its own Tests checks is #132.

## cody, 2026-11-26T09:50:20-08:00

Status: all repos call the shared jobs (see the comment above). Open: the copied leftovers (each repo's ci.yml and ai-review.yml callers, issue templates, issue-archive.yml) have no drift check. Agreed next step: a scheduled job in project-rules that compares each house repo's copies with main and fails or reports on a difference; several private repos ci.yml are intended variants (own Lint and Secrets) and need their own expected form. No open PRs, crons or holds. Handing over to a fresh Claude session.

## cody, 2026-11-26T09:55:25-08:00

The drift check is now its own issue: #141 (baseline of all 14 repos, plan, and the read-token scope waiting on Cody).
