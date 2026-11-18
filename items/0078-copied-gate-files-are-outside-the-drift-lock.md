# #78 Copied gate files are outside the drift lock

- Kind: issue, state: open, by cody, created 2026-11-17T08:41:25-08:00
- Labels: status:ready, type:feature; milestone: none

tools/vendor.py and STANDARD.lock cover shared/ only. The gate workflows, .forgejo/scripts, issue templates and .forgejo/RULES.md that each consumer copies (docs/adopting.md) carry no source tag and no drift check, so an in-place edit in a consumer is invisible and nobody can tell which version a copy came from. Extend vendoring to them so adoption and re-sync are mechanical. Found adopting appliance-job-monitor (#73).

## cody, 2026-11-17T12:30:34-08:00

Also: `.github/workflows/mirror-lockdown.yml` (#89) lacks the `# Canonical copy: SisyphusMD/project-rules; repos get a copy.` header the other copied workflows carry, so a consumer's copy doesn't say where it comes from. Add it when this drift lock lands (a header change means every consumer re-copies).
