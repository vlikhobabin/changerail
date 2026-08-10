## ADDED Requirements

### Requirement: Consumer lock public schema
ChangeRail MUST publish `schemas/changerail-consumer-lock.schema.json` with id
`changerail.consumer-lock.v1` and include it in schema inventory, verifier
wiring and contract smoke.

#### Scenario: Valid consumer lock is checked
- **WHEN** a lock records a supported version/revision, source, wiring profiles
  and `advisory` or `strict` enforcement
- **THEN** schema validation succeeds

#### Scenario: Lock contains unsafe or incomplete source data
- **WHEN** a lock omits exact revision, contains an absolute machine path or a
  credential-bearing source URI
- **THEN** schema or semantic validation fails closed

#### Scenario: Schema inventory is incomplete
- **WHEN** a bootstrapped locked consumer lacks the consumer-lock schema
- **THEN** `verify-project` reports the missing public contract as blocking
