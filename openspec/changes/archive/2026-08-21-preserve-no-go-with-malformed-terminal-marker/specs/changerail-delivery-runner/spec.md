## MODIFIED Requirements

### Requirement: Review-gated safety-stop fallback
The runner MUST fail closed when structured child evidence does not prove that
review-gated publish completed. A schema-valid canonical negative verdict MUST
remain a conservative terminal signal when no authoritative terminal event
exists or when the only conflicting child evidence is a malformed terminal
reason. Every positive verdict MUST remain bound to the exact current tree and
MUST NOT authorize this override.

#### Scenario: Schema-valid no-go overrides malformed child reason
- **WHEN** an unpublished card has a schema-valid canonical verdict with
  `result: no-go`
- **AND** the child emits authoritative `terminal_outcome: BLOCKED` with a
  malformed `terminal_reason`
- **THEN** the runner records terminal outcome `NO-GO`
- **AND** it does not publish the payload

#### Scenario: Malformed child reason without valid negative verdict
- **WHEN** the child emits authoritative `terminal_outcome: BLOCKED` with a
  malformed `terminal_reason`
- **AND** no schema-valid canonical `result: no-go` verdict applies
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: malformed_terminal_reason`
- **AND** it does not publish the payload

#### Scenario: Positive verdict cannot override malformed child reason
- **WHEN** the child emits authoritative `terminal_outcome: BLOCKED` with a
  malformed `terminal_reason`
- **AND** a canonical verdict is positive, stale or invalid
- **THEN** the runner remains fail-closed
- **AND** no commit or push is authorized

#### Scenario: Schema-valid no-go verdict after child exit
- **WHEN** Codex exits without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict for that card validates schema and
  semantic consistency with `result: no-go`
- **THEN** the runner records `NO-GO`
- **AND** the wrapper exits non-zero

#### Scenario: Invalid verdict or stale go after child exit
- **WHEN** Codex exits without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict is invalid, or has `result: go` and fails
  current-tree freshness checks
- **THEN** the runner records `BLOCKED`
- **AND** `terminal_reason` is `review_verdict_invalid`
- **AND** the wrapper exits non-zero

#### Scenario: Unpublished card without verdict after successful child exit
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** no canonical review fallback applies
- **AND** the current card is not uniquely published under
  `openspec/board/4.done`
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: unpublished_card`
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
