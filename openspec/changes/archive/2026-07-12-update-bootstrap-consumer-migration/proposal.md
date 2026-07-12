## Why

New and existing consumer projects must wire directly to ChangeRail after the
rename. Bootstrap, verify and smoke tooling need to generate and enforce the new
paths instead of preserving stale OPSX wiring.

## What Changes

- **BREAKING**: Update bootstrap templates and symlink plans to use
  `/opt/changerail`, `.claude/commands/changerail`, `changerail-*` skills and
  `bin/changerail-*` helpers.
- **BREAKING**: Update `verify-project` to check ChangeRail wiring instead of
  OPSX wiring.
- Rename template placeholders such as `{{OPSX_ROOT}}` to
  `{{CHANGERAIL_ROOT}}`.
- Update wiring, compatibility, migration and consumer adoption runbooks.
- Update release CI and smoke scripts to create and validate generated
  ChangeRail consumers.
- Document the operator sequence for GitHub repository rename and local remote
  update.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-bootstrap`: generate ChangeRail consumer projects and helper
  wrappers.
- `changerail-project-templates`: render ChangeRail project docs, config and OpenSpec
  skeleton references.
- `changerail-project-verification`: verify ChangeRail consumer wiring and config.
- `changerail-wiring-discovery`: update consumer-example smoke for ChangeRail
  command/skill discovery.
- `changerail-release-ci`: run release smoke against generated ChangeRail fixtures.
- `changerail-drift-gate`: classify and report ChangeRail consumers after the rename.

## Impact

- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/**`
- `scripts/smoke-*`
- `.github/workflows/opsx-ci.yml`
- `docs/wiring-discovery.md`, `docs/compatibility.md`,
  `docs/migration-guide.md`, `docs/consumer-adoption-runbook.md`
- Generated consumer projects and existing consumers need one-time migration.
