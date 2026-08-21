## Context

Investigation сохранила `.changerail/source-classification.yaml` единственным
effective input и ограничила profiles provenance/materialization.

## Goals / Non-Goals

**Goals:** publish exact source with ceiling 500.

**Non-Goals:** implement profiles or add another effective rules source.

## Decisions

- Protocol true covers exact profile/check/provenance boundary only.
- One canonical normalization path is mandatory.
- Over-ceiling or second rules source requires split/new investigation.

## Risks / Trade-offs

- **Profile becomes hidden authority.** Effective rules remain in existing
  project file and authorization does not permit implicit override.
