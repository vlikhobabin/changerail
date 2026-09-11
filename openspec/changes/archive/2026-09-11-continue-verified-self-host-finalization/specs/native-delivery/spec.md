## ADDED Requirements

### Requirement: Continue a verified bound finalization
Runtime SHALL retain exact history and frozen project inputs while explicitly transitioning a terminal self-host finalization to a verified replacement engine.

#### Scenario: Explicit engine replacement
- **WHEN** the operator supplies a verified new snapshot and the exact previous engine identity while no delivery writer is live
- **THEN** an append-only before/after receipt and atomic binding replacement are reconciled idempotently without modifying predecessor runs or granting ordinary resume on changed identity.

#### Scenario: Empty exact payload
- **WHEN** an explicitly selected terminal self-host run has a clean payload exactly matching its retained manifest and execution identity
- **THEN** ordinary continuation preserves its completed groups and review accounting and executes the remaining lifecycle gates.

#### Scenario: Unsafe transition
- **WHEN** engine or project inputs drift, the requested previous identity differs, or another writer owns delivery
- **THEN** transition fails closed without a second binding decision or rewritten run evidence.
