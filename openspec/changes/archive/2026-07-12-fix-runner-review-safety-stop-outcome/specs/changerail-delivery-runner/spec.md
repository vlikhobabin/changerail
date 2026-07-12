## MODIFIED Requirements

### Requirement: Explicit terminal outcomes
The runner MUST report terminal outcomes `DELIVERED`, `NO-GO` and `BLOCKED`
without relying on free-text log interpretation.

#### Scenario: Codex exits successfully
- **WHEN** the non-interactive delivery command exits `0`
- **AND** Codex JSONL contains no authoritative terminal outcome
- **AND** structured workspace evidence contains no review-gated safety stop,
  stale verdict, invalid verdict, no-go verdict or blocked publish evidence
- **THEN** the runner records `DELIVERED`

#### Scenario: Codex exits unsuccessfully
- **WHEN** the non-interactive delivery command exits non-zero
- **THEN** the runner records `BLOCKED` unless structured output identifies
  the result as `NO-GO`

#### Scenario: Structured review event returns no-go
- **WHEN** Codex JSONL contains a structured event such as
  `external-review/no-go`
- **THEN** the runner records and prints terminal outcome `NO-GO`

#### Scenario: Structured review stop awaits external review
- **WHEN** Codex JSONL contains a structured `awaiting-review` event
- **THEN** the runner records and prints terminal outcome `BLOCKED`

#### Scenario: Command run preflight fails
- **WHEN** delivery `run` preflight checks fail before launching Codex
- **THEN** the runner records and prints terminal outcome `BLOCKED`

## ADDED Requirements

### Requirement: Review-gated safety-stop fallback
The runner MUST fail closed when no authoritative terminal event exists and
structured card or review evidence shows that review-gated publish is blocked.

#### Scenario: Fresh no-go verdict after successful child exit
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict for that card validates fresh with
  `result: no-go`
- **THEN** the runner records `NO-GO`
- **AND** the wrapper exits non-zero

#### Scenario: Invalid or stale verdict after successful child exit
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict for that card exists but fails validation
  or freshness checks
- **THEN** the runner records `BLOCKED`
- **AND** the wrapper exits non-zero

#### Scenario: Published card preserves successful fallback
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** the current card has been moved under `openspec/board/4.done`
- **THEN** stale ignored review runtime evidence alone MUST NOT override the
  successful fallback outcome

#### Scenario: Batch supervisor stops after fallback no-go
- **WHEN** a supervisor runs single-card runner invocations sequentially
- **AND** the first runner invocation exits non-zero with `NO-GO` from fallback
  review evidence
- **THEN** the supervisor MUST NOT start the next card in that batch
