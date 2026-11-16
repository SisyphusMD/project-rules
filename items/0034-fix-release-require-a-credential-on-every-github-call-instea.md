# #34 fix(release): require a credential on every GitHub call instead of degrading to unauthenticated

- Kind: issue, state: closed, by cody, created 2026-11-16T14:07:32-08:00
- Labels: pr-record; milestone: none

_Recreated from SisyphusMD/project-standard#14 (pull request, opened by cody on 2026-08-29, merged 2026-08-29). Branch `refs/pull/14/head` into `main`._

Unauthenticated github.com allows 60 requests an hour per IP and every runner, mirror probe and CI poller shares one. Several helpers treated their token as optional, so once the budget was gone they did not fail - they answered 403, and the checks built on them stopped deciding anything while still reporting success. The republish guard did exactly that on its first real run.

Every GitHub caller now makes its token mandatory: push-tag.sh, check-mirror-ci.sh, check-rc-install-matrix.sh, reconcile-releases.sh, github-release.sh. reconcile also authenticates the asset download, which was reaching GitHub bare.

push-tag.sh asserts its token BEFORE `git push --atomic`, since discovering it afterwards would leave the tag published and the run failed - and only when a mirror is configured, so the documented no-project.env mode still pushes.

`tests/test-github-auth.sh` pins all of it, including the shapes that previously slipped through: a credential-free `auth` array that keeps its name, an auth helper whose github arm is gone, a sourced library that drops the inherited array, and the guard being moved below the push. Each has a negative control.
