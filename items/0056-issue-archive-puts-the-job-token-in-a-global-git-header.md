# #56 issue-archive puts the job token in a global git header

- Kind: issue, state: open, by cody, created 2026-11-16T19:37:17-08:00
- Labels: status:ready, type:bug; milestone: none

From a house-model review on 2026-11-16, confirmed on main: issue-archive.yml:26 runs `git config --global http.extraHeader "Authorization: Basic ..."`, so the token rides on every host git contacts for the life of that runner home, and user.name/email stay set. ci.yml already scopes it per command (`git -c http.extraHeader=...`); do the same here, or scope it to the Forgejo URL.
