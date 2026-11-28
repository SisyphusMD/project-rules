# #133 Adopt the project rules on the Humble Pixels Forgejo

- Kind: issue, state: open, by cody, created 2026-11-26T06:40:59-08:00
- Labels: status:needs-decision, type:chore; milestone: none

Cody, 2026-11-26: "sounds like we don't have our best practices from bryantserver repos in our hp repos, huh?" A read-only inventory the same day confirms it.

## Where the Humble Pixels repos stand

A read-only inventory the same day found none of the house standards in the Humble Pixels repos (labels, CONTRIBUTING.md, SECURITY.md, issue templates, issue-archive, CI callers, protection by the rules). Repo-by-repo state: details in the Humble Pixels tracker (private).

## Cross-instance blockers

1. project-rules does not exist on the other git host, and its default actions source would not resolve `uses: SisyphusMD/project-rules/...@main` there; callers need a full URL or a mirror of project-rules.
2. The shared jobs used house-only services (a package index and an LLM endpoint reachable only from the house network). The other host has no home for either yet.
3. Rule 21 named the house git host as primary with a backup mirror; the other instance's primary is its own git host with its own backup. Whether that satisfies rule 21 is a decision.

## Proposed order

1. Decide the cross-instance path (this issue).
2. Mechanical, no runner access needed: labels (fj-issues bootstrap), CONTRIBUTING.md, SECURITY.md, issue templates, issue-archive, a README where one is missing.
3. Pilot CI and AI review on one small active repo, then the rest.
4. Required checks and no-direct-push protection last, after proof runs per docs/adopting.md; site repos keep their pipeline checks alongside.

Not verified (runner reachability and capacity, GitHub mirrors) and the Humble Pixels Mac mini plan: details in the Humble Pixels tracker (private).

## cody, 2026-11-26T06:53:34-08:00

Fit check, 2026-11-26 (Cody asked whether every rule makes sense for Humble Pixels). Most rules apply as written; the five that needed a change are now generic: the scope line, rule 21 (primary and mirror), rules 6 and 19 (preview branch for client sites), rule 15 (AI review exemption until the other host can reach the LLM) and rule 23 (applies unchanged if a repo becomes public). Rule-by-rule detail: details in the Humble Pixels tracker (private).

## cody, 2026-11-26T06:53:40-08:00

Mirror findings, 2026-11-26: the shared workflows locate project-rules through github.server_url, so a plain pull mirror at SisyphusMD/project-rules on the other host works unchanged except for four spots. In project-rules (make generic, house sets its own values): gate-lint downloads pip tools and gitleaks from a house-only package host; review.yml hardcodes LLM_URL to the house cluster proxy; issue-archive commits as issue-archive@noreply.bryantserver.com. On the other host: its default actions source is off-instance, so `uses: SisyphusMD/project-rules/...` and actions/checkout would resolve off-instance; point it at itself and mirror the actions the workflows use, as the house does.

## cody, 2026-11-26T07:15:57-08:00

Design direction, 2026-11-26 (Cody: if HP gets a mirror, project-rules "needs to be fully generalized and abstracted with references to manifests that pull the details for the environment"). project-rules stays byte-identical on every Forgejo and names no instance. Rule 21 becomes "a repo's primary is the forge it lives on, push-mirrored to the backup forge in its instance manifest"; rule 15 makes AI review required unless the instance manifest exempts it citing an open issue; the client-site staging flow becomes a generic rule (a repo may declare a preview branch in CONTRIBUTING.md; main then only takes promotion PRs of a commit that passed the preview checks). Each Forgejo keeps its own unmirrored manifest with backup_forge, llm_url, ai_review, package_index, release_mirror and bot_email; workflows read it via github.server_url. HP Forgejo also needs DEFAULT_ACTIONS_URL pointed at itself plus mirrors of the actions used. Open: manifest as a small per-instance repo (recommended, e.g. SisyphusMD/forge-env with env.json) or Forgejo Actions variables.

## cody, 2026-11-26T07:24:10-08:00

Decision direction, Cody 2026-11-26: "Yes small repos." One manifest repo per owner (SisyphusMD, bryantserver, cody on the house instance; the Humble Pixels owner on its own host); a workflow reads the manifest of the owner of the repo it runs in, no layering; a project-rules test flags drift between owners where values should match. Rules text and manifest keys say "git host" and "mirror", not Forgejo or forge ("in case anyone doesn't use Forgejo"); workflows stay Actions workflows; the house Forgejo API helpers stay Forgejo-specific tooling. Name pending (offered: .project-rules, .rules-env, .git-host).

## cody, 2026-11-26T07:33:28-08:00

Decisions, Cody 2026-11-26: per-owner manifest repo name is `<owner>/.project-rules` (each owner keeps its own, never mirrored). Canonical rules stay at SisyphusMD/project-rules on the house git host; the HP host keeps a read-only pull mirror at the same path (a SisyphusMD org holding only that mirror), so caller `uses:` lines and the gate clone from github.server_url are identical on both hosts. Anonymous sync since the repo is public; if the house is down HP CI runs on the last synced rules.

## cody, 2026-11-26T07:52:36-08:00

Decision, Cody 2026-11-26: the Humble Pixels owner's `.project-rules` starts with ai_review exempt, citing an open issue, until the Mac mini ci VM (the Humble Pixels Mac mini issue, private tracker) can reach the Studio LLM through one firewall exception; then AI review turns on. Technical call (Claude): the rules scope line becomes "every repository whose owner keeps a .project-rules manifest", so no instance or org is named.

## cody, 2026-11-26T08:51:02-08:00

Decision, Cody 2026-11-26 ("I trust your thoughts"): a generic preview-branch rule. A repo may name a preview branch in its CONTRIBUTING.md (client sites: `staging`). Changes, Renovate included, land on it through PRs and the required checks; `main` then only takes promotion PRs that pin a commit which passed the preview checks and was approved. Direct pushes to the preview branch stop.

Technical call (Claude): RULES.md keeps its absolute links to the canonical copy on the house git host; a link to the canonical source is not an instance dependency in the workflows.

## Build order (one issue + PR each, per the rules)

1. project-rules: generic wording (scope line, rule 21 primary/mirror, rule 15 manifest exemption, preview-branch rule, git host not Forgejo); workflows read `<owner>/.project-rules/env.json` via github.server_url for mirror_url, llm_url, ai_review, package_index, release_mirror, bot_email; schema test plus a drift test across owners. House behaviour unchanged.
2. House manifests: SisyphusMD/.project-rules, bryantserver/.project-rules, cody/.project-rules with today's values, landed before step 1 merges so the house never runs without one.
3. HP git host (the Humble Pixels tracker, private): the default actions source pointed at itself, mirrors of the actions the workflows use, a SisyphusMD org holding a pull mirror of project-rules, the Humble Pixels owner's `.project-rules` (ai_review exempt citing the AI-review issue).
4. HP repos, mechanical: labels, CONTRIBUTING.md (with each repo's tests and preview branch), SECURITY.md, issue templates, issue-archive, missing README.
5. HP CI callers: pilot on one small active repo, then the rest.
6. Protection last, after proof runs: no direct pushes on main, required checks.
7. AI review on HP when the Mac mini ci VM reaches the Studio LLM (the Humble Pixels Mac mini issue, private tracker).

## cody, 2026-11-26T09:53:02-08:00

Technical call: The three manifest repos (SisyphusMD, bryantserver and cody `/.project-rules`) are public, with issues and pull requests on and wiki, projects, releases and packages off. Each gets a README naming every key and what reads it, a CONTRIBUTING.md from the template (its test is `manifest.py check env.json`; all of env.json is safety-critical; break-glass for a broken main), SECURITY.md copied from the template, the nine generic labels and the backup push mirror. No GitHub copy. CI callers, issue-archive and main protection come once the workflow switch (#136) is on main, since their checks read the manifest and protection needs the proof runs adopting.md asks for. Why: The manifest is trusted input: package_index decides what every pull_request_target Lint job installs and llm_url where private diffs go, so it gets the same issue, PR and protection path as any repo, and Cody is the only account that can push. It holds no secrets and the values are already public in project-rules. Public, because the job token cannot read a private repo; a GitHub copy would publish nothing useful and needs Cody's yes.

Decided by: Claude, 2026-11-26.

## cody, 2026-11-26T09:53:02-08:00

Technical call: The shared jobs clone the owner's manifest with the job token, not anonymously, and the hostname test covers `.forgejo/` (workflows, scripts, issue templates) and `tools/`. `shared/packaging/` release tooling and `.github/workflows/mirror-lockdown.yml` still name forgejo.bryantserver.com and stay out of the test. Why: Probed 2026-11-26: a public repo in a private org is unreadable both ways, in a limited-visibility org it is readable with the job token only, and public owners work both ways, so the token is the one path that works for every owner. The release tooling only publishes the house's public SisyphusMD projects and mirror-lockdown runs on GitHub, not on a mirrored git host, so generalising them is separate work for when another host needs them.

Decided by: Claude, 2026-11-26.

## cody, 2026-11-26T09:53:03-08:00

Technical call: The drift check lives in project-rules' own Tests workflow (job `The owner manifests can be read and agree`), with the house owners listed there (SisyphusMD, bryantserver, cody), and runs the same read step the shared jobs run with the branch's reader. Why: project-rules is canonical on the house git host and its Tests workflow never runs in other repos or on a pull mirror, so the list names no instance in any file another repo runs. A networked pytest would fail offline and hide the real runner path.

Decided by: Claude, 2026-11-26.

## cody, 2026-11-26T09:53:03-08:00

Technical call: An AI review exemption passes only while the cited reference is an open issue the job token or ISSUE_READ_TOKEN can read; a closed issue fails the check and asks for the review back, an unreadable one or a pull request errors. So an owner-wide exemption should cite an issue every repo under that owner can read, such as one in `<owner>/.project-rules`, which can link the real blocker (for Humble Pixels, the Mac mini issue in its private tracker). A pass already posted stays on its head when the issue later closes, like any other check result. Why: Rule 15 says citing an open issue; checking it at run time keeps the exemption from outliving its reason. A private cross-repo issue is unreadable without a read token, and failing closed there is the rule-15 default.

Decided by: Claude, 2026-11-26.

## cody, 2026-11-26T09:53:03-08:00

Technical call: The preview-branch rule is folded into rules 6 and 19 instead of becoming a new rule, and rule 15 now says the checks run the workflow from the protected branch a PR targets. Why: Rules 21 to 23 are cited by number across every repo, so no rule is renumbered. Forgejo runs pull_request_target workflows from the PR's target branch, so a preview PR is judged by the preview branch's callers; adopting.md says to protect the preview branch and add it to ci.yml's branches. MODEL stays in review.yml: it is not one of the decided manifest keys and names no host.

Decided by: Claude, 2026-11-26.

## cody, 2026-11-26T10:05:06-08:00

Status, build steps 1 and 2 (2026-11-26):

Step 2, manifests: SisyphusMD/.project-rules, bryantserver/.project-rules and cody/.project-rules exist (Forgejo accepts the dot-leading name), public, each with env.json holding today's values (mirror_url the house mirror host, the llm_url review.yml had, ai_review "required", the two package-host values gate-lint had, the issue-archive bot address), README, CONTRIBUTING, SECURITY and the generic labels. All three pass `manifest.py check` and `drift`. Correction to the first Technical call above: push access is not Cody alone; other org members may have it through teams, which main protection will settle.

Step 1: #134 merged in #138 (the reader), #137 merged in #139 (preview-branch rule, git host wording). #136, the workflow switch, is PR #140, open and held.

Blocked:
1. The bryantserver org's visibility is private, so its job tokens cannot read bryantserver/.project-rules (403). Merging #140 now would break Lint, Secrets and AI review in every bryantserver repo. Needs Cody's call (details on #136).
2. Backup push mirrors for the three manifest repos: the documented a private repo procedure needs a throwaway a private repo admin token minted over SSH, which the permission system refused. The a private repo repo cody/.project-rules exists, empty; the two org repos and the repo-scoped mirror tokens still need that token.

After #140 merges: a consumer proof PR, then CI callers, issue-archive and protection for the manifest repos.

## cody, 2026-11-26T18:28:32-08:00

Decision, Cody 2026-11-26: owner manifests may hold sensitive data, so every `.project-rules` manifest repo is private (nothing under cody is public; SisyphusMD stays fully public and holds nothing private). Done: SisyphusMD, bryantserver and cody `.project-rules` set private 2026-11-26. Workflows read them with a dedicated read-only bot token stored once per owner as an Actions secret, not the job token; no org visibility change. Supersedes the "public manifests" technical call above.

## cody, 2026-11-26T20:15:31-08:00

Decision, Cody 2026-11-26 ("I trust your decision"): manifests carry owner keys as well as host keys. Owner keys: `visibility` (public or private: what repos under the owner may be; a nightly check flags violations), `mirrors` (where repos push-mirror; SisyphusMD also mirrors to GitHub), `decided_by` (rule 2 deciders: SisyphusMD and cody: Cody; bryantserver and humblepixels: Cody and Anna), `bot_email` (per-owner noreply). Host keys (llm_url, ai_review, package_index, release_mirror) repeat per owner; the drift check compares host keys only, among owners on the same git host. Owners on the house host: SisyphusMD, bryantserver, cody, humblepixels.

## cody, 2026-11-26T20:35:54-08:00

Status: step 1 continues in #140 (reworked for private manifests read by a reader bot, the owner keys, and the Owners drift and visibility checks; details on #136). New blocker #143: the reader bot and its secrets, then every caller mapping `PROJECT_RULES_TOKEN`, before #140 merges. Step 2: four private manifest repos on the house host (SisyphusMD, bryantserver, cody, humblepixels) with the new schema; their backup mirrors still wait on the refused backup-host admin token.

## cody, 2026-11-26T22:36:20-08:00

Status: step 1 is merged (#140, with #143 for the bot, its secrets and every consumer mapping them; a proof per owner is on #143), and step 2 holds four private manifests (SisyphusMD, bryantserver, cody, humblepixels) with owner and host keys. Still open: backup-host mirrors of the manifest repos, waiting on the refused backup-host admin token; the visibility check cannot see a private repo under a public owner; and runner infrastructure hostnames in public job logs (#142).

## cody, 2026-11-27T15:08:42-08:00

Status: step 3 is done on the second git host. It has a pull mirror of this repo, the action mirrors, its private owner manifest, a restricted reader bot and the PROJECT_RULES_TOKEN secret. Shared jobs now fetch project-rules with the job token (#152), which a host that requires sign-in needs. Next: step 4 (callers and mechanical files on that host's repos), owned by the Mac mini session.


## cody, 2026-11-27T15:47:55-08:00

Status, 2026-11-27 (session rotating): step 4 is next and owned by the orchestrator session that succeeds this one. It covers the mechanical files and callers on the second host's repos: generic labels, CONTRIBUTING, SECURITY with the owner's own contact, issue templates, callers byte-identical to main with the PROJECT_RULES_TOKEN mapping, the shared issue-archive caller, and a Renovate rule leaving project-rules unpinned where pinDigests is set (as bryantserver/annex#130). Then step 5 (CI pilot), step 6 (protection) and step 7 (AI review, later). No PRs open, nothing running.


## cody, 2026-11-27T18:35:18-08:00

Status, 2026-11-27: steps 4 and 5 are done on the second git host. The pilot repo proved every CI job on pull_request_target, a deliberate failure and recovery, the manifest read and the issue archive. AI review needed a read:issue token so the review job can read the owner-wide exemption issue: the reader bot now has one as the owner's ISSUE_READ_TOKEN, and its team grants issues read on the manifest repo only. All of that owner's non-content repos now carry the callers, CONTRIBUTING, SECURITY and templates. Its client content repos stay file-free by the owner's decision, with their checks to run from its pipeline repo (private tracker). Renovate does not detect the reusable-workflow callers, so the no-pin packageRule is a backstop. Next: step 6, protection, after each repo's proof runs. Details in the private tracker.
