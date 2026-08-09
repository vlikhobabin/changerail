## Why

ChangeRail currently proves the repository-knowledge wiring with a minimal
catalog, but not the full deterministic maintenance harness. The project needs a
public-safe dogfood scope and fixtures that exercise enabled detectors without
turning optional or agent-only signals into hard failures.

## What Changes

- Extend `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` and the
  generated index for the accepted ChangeRail knowledge scope.
- Enable applicable deterministic built-in detectors for dogfood scans.
- Add public-safe regression fixtures for broken links and anchors, stale
  generated index, optional schema-bound instruction producer import and
  canonical source contradiction annotation.
- Keep semantic contradiction as retained agent annotation evidence rather than
  a deterministic scan failure.
- Keep instruction bytes `unknown` until card `050` publishes the producer
  contract.
- Preserve read-only default scan and report behavior.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: the ChangeRail repository dogfoods the
  maintenance harness with non-zero deterministic detector coverage and
  public-safe fixtures.

## Impact

- Affected public surfaces: `.changerail/knowledge.yaml`,
  `.changerail/maintenance.yaml`, generated knowledge index,
  `scripts/changerail_maintenance.py`, fixtures, repository-knowledge specs and
  smoke tests.
- Default CI remains independent of ignored local runtime history.
