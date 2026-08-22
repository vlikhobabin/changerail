## Context

Investigation ограничила payload explicit owner lineage и derived rollup без
raw-log reconstruction.

## Goals / Non-Goals

**Goals:** publish exact source with aggregate ceiling 500.

**Non-Goals:** implement metrics or authorize content-bearing telemetry.

## Decisions

- Runner lineage production budget <=300; metrics production budget <=200.
- Protocol allowance only covers exact owner/derived schemas.
- Over-budget or raw-log scope requires split/new investigation.

## Risks / Trade-offs

- **One side consumes entire budget.** Aggregate preflight ceiling remains
  authoritative and forces a split.
