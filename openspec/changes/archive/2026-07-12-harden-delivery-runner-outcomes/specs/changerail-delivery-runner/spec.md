## ADDED Requirements

### Requirement: Authoritative terminal events для delivery runner
Delivery runner MUST выводить `NO-GO` и `BLOCKED` terminal outcomes только из
documented structured event types или explicit terminal outcome fields и MUST
NOT рекурсивно интерпретировать arbitrary JSON string values как terminal
outcomes.

#### Scenario: Non-terminal tool error перед successful exit
- **WHEN** Codex JSONL содержит non-terminal tool result со string values вроде
  `error` или `failed`, а process завершается `0`
- **THEN** runner записывает `DELIVERED`

#### Scenario: Authoritative no-go event
- **WHEN** Codex JSONL содержит documented structured no-go event
- **THEN** runner записывает и печатает terminal outcome `NO-GO`

#### Scenario: Awaiting review event
- **WHEN** Codex JSONL содержит documented `awaiting-review` или
  `awaiting-external-review` event
- **THEN** runner записывает и печатает terminal outcome `BLOCKED`

#### Scenario: Conflicting terminal events учитывают order
- **WHEN** Codex JSONL содержит несколько authoritative terminal events
- **THEN** runner использует последний authoritative terminal event в stdout
  order

#### Scenario: Non-zero exit без authoritative outcome
- **WHEN** Codex завершается non-zero и stdout не содержит authoritative
  terminal outcome
- **THEN** runner записывает `BLOCKED`
