## Context

Maintenance behavior is already implemented across CLI commands, schemas,
skills, examples and specs. Operators can discover pieces in
`docs/changerail-contracts.md`, `docs/consumer-adoption-runbook.md`,
`examples/maintenance/` and the `changerail-maintain` skill, but there is no
single public runbook for the safe consumer workflow.

## Goals / Non-Goals

**Goals:**
- Publish one Russian runbook for the complete maintenance lifecycle.
- Link the runbook from the main documentation flow.
- Update contract reference docs for feedback, quality and full schema
  inventory.
- Keep read-only defaults and explicit writes visibly separate.

**Non-Goals:**
- Add new CLI behavior beyond documentation corrections.
- Grant scheduled workflows write authority.
- Document private deployment or machine-local setup.

## Decisions

1. Add a dedicated maintenance operations runbook under `docs/`. The runbook
   is operator-facing and procedural, while `docs/changerail-contracts.md`
   remains the reference for wire contracts and schema semantics.

2. Use generic POSIX examples as the primary command form and native Windows
   equivalents only where the current surface has `.cmd` wrappers. This avoids
   implying unsupported Windows shell coverage for helper surfaces that do not
   have native wrappers.

3. Index scheduler examples rather than embedding all YAML/service content in
   the runbook. The runbook should explain prerequisites, least privilege and
   safe use, while the files under `examples/maintenance/` stay as copyable
   examples.

## Risks / Trade-offs

- [Risk] A long runbook could duplicate contract reference details and drift.
  Mitigation: keep schemas and exact field semantics in contracts docs; runbook
  links to reference sections.
- [Risk] Scheduler docs could imply mutation authority. Mitigation: every
  scheduler path states read-only default behavior and separates write-capable
  follow-up workflows.
- [Risk] Windows examples could overclaim support. Mitigation: include native
  Windows commands only for existing `.cmd` wrappers and otherwise document the
  POSIX/CI surface.
