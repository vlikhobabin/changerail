## Why

Public docs and release notes still describe several implemented surfaces as
planned or omit them entirely. Consumer projects need README, repository
instructions, changelog, compatibility notes and migration guide to reflect the
current ChangeRail product, not an older bootstrap snapshot.

## What Changes

- Update `AGENTS.md` and `README.md` so tracked templates, bootstrap, verify,
  runner, metrics, schemas, finalization helpers and smoke checks are described
  as current public surface.
- Expand `CHANGELOG.md` Unreleased entries to include delivery runner,
  delivery metrics, review history/fingerprint, manifest derivation, public
  scans, aliases and publish finalization behavior.
- Sync compatibility notes and migration guide with user-facing changes after
  `0.1.0`, including operational runner, metrics, manifest/review contracts,
  aliases and finalization behavior.
- Keep drift command documentation clear: no-argument `scripts/smoke-drift.py`
  is not a self-contained smoke; release CI and local baseline use generated
  public-safe fixtures.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-release-discipline`: public release docs, changelog and migration
  notes must describe the actual current release surface and verification
  gates.
- `changerail-agent-methodology`: repository instructions must identify the
  current public ChangeRail-owned surface without stale planned-status claims.

## Impact

- `AGENTS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/release-discipline.md`
- public-safety scan expectations for release documentation
