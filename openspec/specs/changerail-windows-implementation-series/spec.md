# changerail-windows-implementation-series Specification

## Purpose
Зафиксировать planning contract for the refreshed native Windows implementation
series after the `030-03` architecture decision.

## Requirements

### Requirement: Refreshed native Windows implementation series
ChangeRail MUST refresh the native Windows implementation series after the
architecture decision and before delivering any executable `040` story.

#### Scenario: Maintainer reads the refreshed series
- **WHEN** a maintainer reads `040-native-windows-implementation`
- **THEN** the epic and executable cards identify the `030-03` architecture
  decision as their source
- **AND** they no longer describe their planning state as provisional
- **AND** each executable card remains in `1.backlog` until its own readiness
  gate moves it to `2.todo`

### Requirement: Implementation cards preserve architecture boundaries
The refreshed `040` cards MUST decompose native Windows support into ordered,
independently reviewable implementation stories that preserve the selected
default path, bounded fallbacks and verification floor.

#### Scenario: Cards are ordered for delivery
- **WHEN** the refreshed `040` cards are inspected
- **THEN** runtime entrypoints precede Windows wiring
- **AND** wiring precedes verifier, drift and Git safety
- **AND** verification safety precedes automated smoke
- **AND** automated smoke precedes end-to-end support proof

#### Scenario: Card acceptance maps to architecture contract
- **WHEN** a `040` executable card is prepared for delivery
- **THEN** its acceptance and verification sections cover the relevant
  architecture requirements for entrypoints, generated ownership,
  fallback policy, drift/upgrade, cleanup, threat model or test matrix

### Requirement: Implementation refresh excludes runtime changes
The `030-03` backlog refresh MUST NOT implement native Windows runtime behavior.

#### Scenario: Backlog refresh is delivered
- **WHEN** the `030-03` card is implemented and reviewed
- **THEN** the reviewed payload updates architecture docs, OpenSpec specs and
  board planning
- **AND** it does not change helper runtime code, bootstrap behavior,
  verification behavior, templates or smoke implementation
