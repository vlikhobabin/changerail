## MODIFIED Requirements

### Requirement: Authoritative terminal events для delivery runner
Delivery runner MUST выводить `NO-GO` и `BLOCKED` terminal outcomes только из
documented structured event types, explicit terminal outcome fields или exact
terminal marker lines в completed agent-message event и MUST NOT рекурсивно
интерпретировать arbitrary JSON string values как terminal outcomes или
reasons.

#### Scenario: Non-terminal tool error перед published successful exit
- **WHEN** Codex JSONL содержит non-terminal tool result со string values вроде
  `error` или `failed`, process завершается `0`, а карточка опубликована
- **THEN** runner записывает `DELIVERED`

#### Scenario: Authoritative fix-budget handoff
- **WHEN** completed agent-message event содержит exact lines
  `terminal_outcome: BLOCKED` и
  `terminal_reason: fix_budget_exhausted`
- **THEN** runner записывает и печатает оба machine-readable значения
- **AND** завершает wrapper non-zero

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

### Requirement: Review-gated safety-stop fallback
The runner MUST fail closed when no authoritative terminal event exists and
structured card or review evidence does not prove that review-gated publish
completed.

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

### Requirement: Queue fail-fast terminal outcomes
The delivery runner MUST stop launching new downstream cards when a live child
or queue validation reaches an unsafe terminal outcome. Autonomous recovery
after child `NO-GO` or `fix_budget_exhausted` MUST be represented as a linked
rescue/replacement card before dependent downstream cards resume.

#### Scenario: Child returns no-go
- **WHEN** a child delivery run returns `NO-GO`
- **THEN** aggregate queue status records `NO-GO`
- **AND** no new downstream cards are launched

#### Scenario: Child exhausts fix budget
- **WHEN** a child delivery run returns `BLOCKED` with
  `terminal_reason: fix_budget_exhausted`
- **THEN** aggregate queue status preserves that terminal reason
- **AND** no new downstream cards are launched

#### Scenario: Autonomous recovery is represented as a card
- **WHEN** an autonomous agent continues after a terminal child `NO-GO` or
  `fix_budget_exhausted`
- **THEN** it MUST create or run a linked rescue/replacement card carrying
  `recovery_for` rather than pushing the failed child payload
- **AND** dependent downstream cards remain blocked until recovery publishes
  through a fresh independent `GO`

#### Scenario: Child returns blocked
- **WHEN** a child delivery run returns `BLOCKED` for an external or unavailable
  condition
- **THEN** aggregate queue status records `BLOCKED`
- **AND** no new downstream cards are launched or automatic recovery card is
  inferred

#### Scenario: Repository state is inconsistent after child success
- **WHEN** child status reports `DELIVERED` but card location, git cleanliness,
  upstream equality or no-push ahead-state success checks fail
- **THEN** aggregate queue status records `BLOCKED`

#### Scenario: Child status is missing or invalid
- **WHEN** a queue child exits but its delivery-run status is missing or has an
  unsupported result
- **THEN** aggregate queue status records `BLOCKED` with
  `missing_or_invalid_child_status` regardless of process exit code

### Requirement: Safe queue resume
The delivery runner MUST implement `resume-plan` without re-running already
successful queue cards, without trusting unrelated plan drift, and with one
constrained recovery-plan augmentation after a recoverable terminal child.

#### Scenario: Resume sees delivered card
- **WHEN** aggregate status shows a card succeeded and current workspace state
  still satisfies the selected push or no-push success criteria
- **THEN** `resume-plan` skips that card

#### Scenario: Resume sees moved unfinished card
- **WHEN** an unfinished card has moved to another non-canceled board lane
- **THEN** `resume-plan` re-resolves the current card path before launching it

#### Scenario: Plan fingerprint changes without valid recovery augmentation
- **WHEN** the current plan fingerprint differs from aggregate status and the
  change is not limited to valid added `recovery_for` cards
- **THEN** `resume-plan` records `BLOCKED` and exits non-zero before launching
  unfinished cards

#### Scenario: Plan adds a valid recovery card
- **WHEN** a changed plan preserves all previous card identity, workspace, card
  reference, wave and dependencies
- **AND** every added card is a unique same-workspace, same-wave recovery for a
  prior `NO-GO` card or prior `fix_budget_exhausted` card
- **THEN** `resume-plan` accepts the recovery augmentation and launches the
  recovery before dependants of the failed source

#### Scenario: Recovery publishes successfully
- **WHEN** the recovery child returns `DELIVERED` and normal queue publish-state
  checks pass
- **THEN** aggregate status marks the source `recovered` and records
  `recovered_by`
- **AND** only then may the source id satisfy downstream dependencies

#### Scenario: Recovery fails
- **WHEN** the recovery child returns `NO-GO`, `BLOCKED` or inconsistent publish
  state
- **THEN** aggregate queue remains fail-fast and does not launch source
  dependants
