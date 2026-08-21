## MODIFIED Requirements

### Requirement: Explicit terminal outcomes
The runner MUST report terminal outcomes `DELIVERED`, `NO-GO` and `BLOCKED`
without relying on free-text log interpretation, MUST preserve a schema-valid
negative review signal across mandatory post-review rescue handoff mutation,
and MUST require current-tree freshness before accepting any positive verdict.

#### Scenario: Final no-go creates a tracked rescue handoff
- **WHEN** the latest canonical unpublished verdict is schema-valid and has
  `result: no-go`
- **AND** a required tracked rescue or replacement card created after review
  makes the negative verdict fingerprint stale
- **THEN** the runner records terminal outcome `NO-GO`
- **AND** it does not publish the reviewed payload

#### Scenario: Unpublished go verdict is stale
- **WHEN** the latest canonical unpublished verdict has `result: go`
- **AND** its fingerprint, head commit or reviewed tree is not fresh
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: review_verdict_invalid`
- **AND** it does not publish the payload

### Requirement: Review-gated safety-stop fallback
The runner MUST fail closed when no authoritative terminal event exists and
structured card or review evidence does not prove that review-gated publish
completed. A schema-valid negative verdict MUST remain a conservative terminal
signal after tracked rescue handoff mutation, while every positive verdict MUST
remain bound to the exact current tree.

#### Scenario: Schema-valid no-go verdict after child exit
- **WHEN** Codex exits without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict validates schema and semantic
  consistency with `result: no-go`
- **THEN** the runner records `NO-GO`
- **AND** the wrapper exits non-zero

#### Scenario: Invalid verdict or stale go after child exit
- **WHEN** Codex exits without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical verdict is invalid, or has `result: go` and fails
  current-tree freshness checks
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: review_verdict_invalid`
- **AND** the wrapper exits non-zero

### Requirement: One-command delivery regression smoke
ChangeRail MUST include an end-to-end local one-command smoke that exercises
the tracked delivery runner and distinguishes positive verdict freshness from
the conservative final negative-review handoff.

#### Scenario: One-command delivery fails closed on stale go verdict
- **WHEN** the smoke provides a canonical `result: go` verdict whose
  fingerprint, head commit or reviewed tree is stale for an unpublished card
- **AND** the child exits without authoritative delivery evidence
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: review_verdict_invalid`
- **AND** no payload commit is pushed

#### Scenario: One-command delivery preserves exhausted-budget no-go
- **WHEN** the smoke writes a schema-valid final `result: no-go` after the
  same-card rescue budget is exhausted
- **AND** a tracked rescue handoff makes the negative verdict stale
- **AND** the child exits without an authoritative terminal event
- **THEN** the runner records `NO-GO`
- **AND** no payload commit is pushed
