## Context

The release payload is intentionally documentation and metadata only. It
records already-delivered work from commits after `v0.4.0` and makes the
release externally consumable.

## Decisions

### Version

Use `0.5.0`, not `0.4.1`, because the post-`v0.4.0` payload adds and changes
public workflow contracts: maintenance lifecycle, consumer locks, bootstrap
profiles, generated consumer CI and runtime diagnostics.

The OpenSpec change slug is `prepare-0-5-0-release` because OpenSpec change
names allow lowercase letters, numbers and hyphens only.

### Breaking Notes

Record one breaking entry: new consumer bootstrap defaults now render
`safe-interactive` Codex authority. Existing generated consumers are not
rewritten automatically, but unattended bootstrap automation must request
`--codex-policy trusted-automation` explicitly.

### Publication

Publish through a scoped release-prep commit, annotated tag `v0.5.0`, push to
`origin/main` and GitHub release when authenticated `gh` access is available.
Do not claim new live Windows two-host evidence unless a live matrix is run for
this release.

## Verification

Use the repository release baseline:

```bash
python3 scripts/run-release-baseline.py
```

Also retain explicit public-surface current/history scan, strict OpenSpec
validation and whitespace check outcomes in the release card.
