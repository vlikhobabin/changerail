## Why

The maintenance harness exists across CLI commands, schemas, skills, scheduler
examples and reference docs, but a consumer operator has no single runbook for
the full adoption and operation flow. The result is a working toolchain whose
safe usage boundary is discoverable only by reading implementation artifacts.

## What Changes

- Add a public Russian end-to-end maintenance operations runbook for new and
  existing consumer repositories.
- Link the runbook from `README.md`, documentation index/adoption docs and the
  relevant contract references.
- Document first scan, generated index, state, baseline/waiver, audit, triage,
  card handoff, scheduled read-only runs, feedback normalization and quality
  rollup.
- Update contract reference inventory for all maintenance schemas, including
  quality rollup and proposal decision.
- Index scheduler examples with prerequisites and least-privilege limits.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: operator-facing maintenance lifecycle,
  feedback and quality usage are documented as part of the repository knowledge
  harness contract.
- `changerail-contracts`: public contract documentation lists every tracked
  maintenance schema and current feedback/quality surfaces.

## Impact

- Affected files: `README.md`, `docs/changerail-contracts.md`,
  `docs/consumer-adoption-runbook.md`, new maintenance runbook documentation
  and scheduler example references.
- No new mutation authority is introduced. Read-only defaults remain separate
  from explicit writes such as `render-index --write`, `--write-state`,
  baseline write and card write.
