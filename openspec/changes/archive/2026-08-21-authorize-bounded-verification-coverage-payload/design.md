## Context

Investigation выбрала five-field map и derived ledger references вместо второго
acceptance source.

## Goals / Non-Goals

**Goals:** publish exact source with ceiling 500.

**Non-Goals:** implement gates or impose a global check catalog.

## Decisions

- Protocol true applies only to exact map/ledger admission boundary.
- One canonical loader is mandatory.
- Scope expansion or >500 requires split/new investigation.

## Risks / Trade-offs

- **Map duplicates acceptance.** Authorization becomes inapplicable when
  implementation copies acceptance/tasks rather than references.
