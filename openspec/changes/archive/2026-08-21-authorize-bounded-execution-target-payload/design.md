## Context

Deterministic preflight принимает protocol exception только из clean tracked
`4.done` source, bound к exact investigation и successor.

## Goals / Non-Goals

**Goals:** publish one exact authorization object and reciprocal relations.

**Non-Goals:** implement target behavior, raise limits or authorize providers.

## Decisions

- Ceiling остается 500; превышение требует split.
- `allow_new_authority_or_wire_protocol` true покрывает только investigated
  target identity contract.
- Source не содержит runtime evidence или reusable waiver.

## Risks / Trade-offs

- **Path drift invalidates source.** Это намеренный fail-closed binding.
