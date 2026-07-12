## ADDED Requirements

### Requirement: Short alias guidance preserves canonical naming
ChangeRail public methodology and user-facing docs MUST present `chrl-*` and
`/chrl:*` as recommended daily shorthand while preserving `changerail-*` and
`/changerail:*` as canonical reference names.

#### Scenario: Agent reads lifecycle guidance
- **WHEN** an agent reads ChangeRail lifecycle documentation
- **THEN** the guidance shows `chrl-*` or `/chrl:*` as acceptable daily
  invocation shorthand
- **AND** it identifies canonical `changerail-*` or `/changerail:*` commands as
  the source-of-truth contract names

#### Scenario: Runtime contracts are reviewed
- **WHEN** runtime paths, schema ids or OpenSpec namespaces are reviewed after
  alias implementation
- **THEN** they continue to use `changerail` naming
- **AND** no new `chrl` runtime namespace is introduced
