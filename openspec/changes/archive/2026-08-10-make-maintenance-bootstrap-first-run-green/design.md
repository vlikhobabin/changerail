## Context

`bin/bootstrap-project --with-maintenance` currently renders
`.changerail/knowledge.yaml` and `.changerail/maintenance.yaml`, but not the
configured `.changerail/KNOWLEDGE.md` index. The starter policy includes
`.changerail/**/*.yaml` and `openspec/**/*.md` in the scan universe, while the
starter catalog has only two records. A fresh consumer therefore validates the
catalog but fails `render-index --check` and reports uncovered/orphan findings
before an operator has made any project-specific choice.

## Goals / Non-Goals

**Goals:**
- Make the fresh opted-in maintenance skeleton green for
  `validate-catalog`, `render-index --check` and `scan --json`.
- Keep default bootstrap output unchanged when maintenance is not requested.
- Treat the starter index as generated output while preserving project-owned
  catalog and policy customization.

**Non-Goals:**
- Add maintenance `fix` mode or any scheduled write authority.
- Run full maintenance scans inside `verify-project`.
- Create a domain-specific catalog taxonomy for consumer projects.

## Decisions

1. Generate `.changerail/KNOWLEDGE.md` during maintenance opt-in bootstrap.
   This keeps first-run `render-index --check` read-only and green. It also
   avoids making `verify-project` or `scan` perform hidden writes.

2. Add starter catalog records instead of shrinking the configured universe.
   `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` and
   `openspec/board/card-template.md` are real maintenance/board knowledge files
   in a fresh consumer. Covering them documents the opt-in surface and keeps
   `catalog-coverage`/`repository-orphans` semantics unchanged.

3. Keep catalog and policy project-owned after rendering. Bootstrap may render
   their initial content for a new target, but repeat bootstrap or refresh must
   not silently replace consumer customization. Only the generated index has a
   generated-output ownership model.

## Risks / Trade-offs

- [Risk] Rendering an index during bootstrap could drift if the index renderer
  changes. Mitigation: focused smoke must bootstrap a disposable consumer and
  immediately run `render-index --check`.
- [Risk] Starter catalog records could look like a prescribed documentation
  taxonomy. Mitigation: records are limited to ChangeRail starter files needed
  for first-run green behavior and documented as extensible.
- [Risk] Generated-copy Windows wiring has separate ownership metadata.
  Mitigation: first-run index generation stays in template/bootstrap output,
  while helper-copy ownership remains governed by existing generated wiring
  contracts.
