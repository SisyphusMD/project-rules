# #155 Make Copies match a required check

- Kind: issue, state: closed, by cody, created 2026-11-27T20:39:21-08:00
- Labels: type:chore; milestone: none

Cody decided (2026-11-27): "skip it, make it required". An automatic re-copy job is not worth building, since copied files should now change only a few times a year. Instead: add `Copies match` to rule 15's required checks, and a change to a copied file ships with its rollout (a re-copy PR in every repo, merged right after it), because a required Copies match blocks every PR in a repo whose copies are behind. Proven per adopting.md step 5: a passing run on #150 and a real failure on a consumer PR that pinned the callers. Then add the check to each repo's protected main.

## cody, 2026-11-27T20:46:24-08:00

Done: #156 merged (main a216b50). `CI / Copies match (pull_request_target)` is now required on main in the ten house repos that already required the gate checks; every one passed Copies match on main first. The repos that do not yet require the gate checks are tracked separately.
