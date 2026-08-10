## Why

Fresh consumers that explicitly opt in to maintenance currently receive valid
helper wiring but fail the first deterministic maintenance scan because the
generated index is absent and the starter catalog does not cover every file in
the configured knowledge universe. This blocks the documented first-run
operator flow even though the underlying harness is already implemented.

## What Changes

- Generate a deterministic starter `.changerail/KNOWLEDGE.md` during
  `bin/bootstrap-project --with-maintenance`.
- Extend the maintenance starter catalog so `.changerail/knowledge.yaml`,
  `.changerail/maintenance.yaml` and `openspec/board/card-template.md` are
  intentionally covered.
- Keep maintenance artifacts absent when `--with-maintenance` is not supplied.
- Add focused disposable consumer smoke coverage for first-run
  `validate-catalog`, `render-index --check` and `scan --json`.
- Preserve project-owned catalog and policy customization on repeat bootstrap
  or refresh; only generated-owned index output may be updated under an
  explicit ownership contract.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-bootstrap`: opted-in maintenance bootstrap must produce a
  first-run green deterministic maintenance skeleton.
- `changerail-project-templates`: maintenance starter templates include the
  complete generated catalog/policy/index surface needed by the first scan.
- `changerail-repository-knowledge`: generated index and starter catalog
  records are part of the consumer-ready repository knowledge contract.

## Impact

- Affected files: `bin/bootstrap-project`, `templates/project/.changerail/`,
  `scripts/smoke-bootstrap-project.py`, repository-knowledge smokes and specs.
- Consumer impact is opt-in only: default bootstrap and existing consumers
  without maintenance artifacts remain unchanged.
