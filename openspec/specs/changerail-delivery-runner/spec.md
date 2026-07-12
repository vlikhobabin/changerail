# changerail-delivery-runner Specification

## Purpose
Зафиксировать tracked generic runner для non-interactive ChangeRail delivery,
structured runtime status и operational preflight behavior.
## Requirements
### Requirement: Non-interactive delivery runner
ChangeRail MUST provide a tracked generic helper that can launch a non-interactive
delivery run for a single board card without private workspace assumptions.

#### Scenario: Runner starts a card delivery
- **WHEN** an operator invokes the runner with a card path
- **THEN** the helper launches Codex non-interactively with instructions to run
  `$changerail-deliver <card-path>` for that card
- **AND** when `--workspace` is omitted, the requested workspace resolves to
  the invocation repository root, or the current working directory outside git
- **AND** the child process runs with cwd and `CODEX_WORKDIR` set to the
  requested workspace
- **AND** absent an explicit operator `CODEX_HOME`, the child uses
  `<workspace>/.codex`

### Requirement: Closed stdin execution
The runner MUST close stdin for the child process it launches.

#### Scenario: Runner runs in background
- **WHEN** the helper starts `codex exec`
- **THEN** the child receives closed or null stdin and cannot block waiting for
  inherited terminal input

### Requirement: Per-run Codex overrides
The runner MUST support per-run `model` and `reasoning_effort` overrides using
standard Codex CLI options while preserving existing defaults when overrides are
absent.

#### Scenario: Operator sets model and effort
- **WHEN** the operator passes model and reasoning effort options
- **THEN** the child Codex command includes those overrides for that run only

#### Scenario: Operator omits overrides
- **WHEN** the operator passes no model or reasoning effort
- **THEN** the runner does not modify repository default model configuration

### Requirement: Structured runtime status
The runner MUST atomically write a machine-readable runtime status or run record
with card, phase, result, timestamps, terminal outcome and commit when
available.

#### Scenario: Supervisor polls status
- **WHEN** a delivery run starts, changes phase or terminates
- **THEN** `<workspace>/.runtime/changerail/delivery-runs/<run-id>/status.json`
  contains the latest structured state without requiring log scraping unless
  `--runtime-root` is explicitly supplied
- **AND** the record contains the workspace `HEAD` as `commit` when available

### Requirement: Runner captures delivery performance summary
The delivery runner MUST record best-effort performance data from child JSONL
events and workspace runtime evidence in the delivery run status record.

#### Scenario: Child emits command lifecycle events
- **WHEN** a fake child JSONL stream contains command start and completion
  events for multiple commands
- **THEN** the runner status includes command execution count
- **AND** it includes command duration summaries with runner-observed durations

#### Scenario: Child emits agent messages
- **WHEN** a child JSONL stream contains agent message events
- **THEN** the runner status includes an agent message count when that event
  class is observed

#### Scenario: Child reaches terminal outcome
- **WHEN** a child JSONL stream or fallback evidence determines a terminal
  outcome
- **THEN** the runner status includes the terminal outcome and available timing
  summary without changing the existing `DELIVERED`, `NO-GO` or `BLOCKED`
  semantics

### Requirement: Runner timestamps observed JSONL events
The delivery runner MUST preserve runner-observed timing for child JSONL events
used in performance summaries.

#### Scenario: Timeline is retained
- **WHEN** the runner records a timeline entry or equivalent command summary
- **THEN** each retained event has a runner-observed timestamp or duration
  derived from runner observation order
- **AND** raw child stdout remains ignored runtime evidence

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

### Requirement: Delivery runner preflight
The runner MUST provide a preflight mode that checks the Codex launcher,
effective `CODEX_HOME`, auth state, `CODEX_HOME` config, stale symlinks,
executable permissions and optional connectivity URL.
Delivery runner preflight MUST sanitize connectivity diagnostics before writing
structured runtime status.

#### Scenario: Connectivity check is requested
- **WHEN** an operator supplies a connectivity URL for preflight
- **THEN** the runner performs an actual connection attempt and records pass or
  fail in structured output

#### Scenario: Auth or wiring is stale
- **WHEN** auth markers are absent or `CODEX_HOME` contains broken symlinks
- **THEN** preflight records explicit diagnostics before the delivery child is
  launched

#### Scenario: Connectivity success is sanitized
- **WHEN** an operator supplies a connectivity URL containing URL userinfo or
  token-like query values and the request succeeds
- **THEN** the structured preflight check records only sanitized endpoint
  metadata and response status
- **AND** it does not include the raw submitted URL, userinfo or query value

#### Scenario: Connectivity failure is sanitized
- **WHEN** an operator supplies a connectivity URL containing URL userinfo or
  token-like query values and the request fails
- **THEN** the structured preflight check records sanitized endpoint metadata
  and the exception class
- **AND** it does not include the raw submitted URL or raw exception text

### Requirement: ChangeRail delivery runner namespace
The non-interactive delivery runner MUST use ChangeRail command, schema and
runtime names after the rename.

#### Scenario: Runner starts a delivery
- **WHEN** the post-rename runner is invoked for a board card
- **THEN** it launches the ChangeRail delivery skill through
  `$changerail-deliver <card-path>`
- **AND** it writes status records using the `changerail.delivery-run.v1`
  schema id

#### Scenario: Runtime root is defaulted
- **WHEN** the runner is invoked without an explicit runtime root
- **THEN** status and logs are written under `.runtime/changerail/delivery-runs`

### Requirement: Runner remains a single-card launcher
The tracked non-interactive delivery runner MUST treat its positional `card`
argument as one card path and MUST NOT imply that it owns multi-card queue
semantics unless explicit queue support is implemented.

#### Scenario: Operator reads runner help
- **WHEN** an operator runs `bin/changerail-delivery-runner run --help`
- **THEN** the help text describes the positional argument as a single
  repository-relative board card path

#### Scenario: Supervisor reads run status
- **WHEN** the runner writes
  `.runtime/changerail/delivery-runs/<run-id>/status.json`
- **THEN** the status record represents the single card passed to that runner
  invocation

### Requirement: Queue semantics belong to deliver or future queue runner
Documentation MUST state that directory or ordered-card queue handling belongs
to `$changerail-deliver` itself, or to a future queue-aware runner with
per-card records.

#### Scenario: Batch delivery is documented
- **WHEN** docs describe bounded batch delivery
- **THEN** they distinguish `$changerail-deliver <board-column>` from
  `bin/changerail-delivery-runner run <single-card>`
