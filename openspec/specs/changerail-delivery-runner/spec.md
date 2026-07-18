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

### Requirement: Queue plan input contract
The delivery runner MUST accept queue plans only through the explicit
`changerail.delivery-plan.v1` contract and MUST preserve existing single-card
runner compatibility.

#### Scenario: Single-card runner remains compatible
- **WHEN** an operator invokes `bin/changerail-delivery-runner run <card>`
- **THEN** the positional card argument is still treated as one card path
- **AND** no queue semantics are inferred from that command

#### Scenario: Queue plan is schema-backed
- **WHEN** an operator invokes a plan-oriented command
- **THEN** the runner validates the plan against
  `schemas/changerail-delivery-plan.schema.json` before applying queue
  semantics

#### Scenario: Queue status is schema-backed
- **WHEN** the runner writes aggregate queue status
- **THEN** the JSON uses `changerail.delivery-plan-status.v1` and validates
  against `schemas/changerail-delivery-plan-status.schema.json`

### Requirement: Queue plan public-safety constraints
The delivery runner MUST fail closed on queue plan values that would put
credentials, secrets or machine-specific tracked state into public plans or
status.

#### Scenario: Workspace path is absolute
- **WHEN** a queue plan workspace path is an absolute machine path
- **THEN** plan validation fails before any child delivery can launch

#### Scenario: Runtime status references logs indirectly
- **WHEN** aggregate queue status includes child evidence
- **THEN** it references structured child status paths and does not inline raw
  stdout or stderr logs

### Requirement: Plan-oriented dry-run commands
The delivery runner MUST provide explicit plan-oriented commands that resolve a
queue plan without launching live child deliveries.

#### Scenario: Operator lists a plan
- **WHEN** an operator invokes `bin/changerail-delivery-runner plan <plan.json>`
- **THEN** the command prints or writes resolved workspaces, card ids, current
  card locations, dependencies, waves and the single-card runner commands that
  would be launched
- **AND** no child delivery process is started

#### Scenario: Plan command honors no-push mode
- **WHEN** an operator passes `--no-push` to a plan-oriented dry run
- **THEN** the resolved child commands include the corresponding delivery
  argument that will be passed to each single-card invocation

### Requirement: Queue preflight validation
The delivery runner MUST fail closed during `preflight-plan` before launching
any live child delivery when plan, workspace, git or card state is inconsistent.

#### Scenario: Plan has invalid dependency graph
- **WHEN** a plan contains a dependency cycle, missing dependency id or
  dependency that points to an invalid later wave
- **THEN** `preflight-plan` records `BLOCKED` aggregate status and exits
  non-zero before any child launch

#### Scenario: Plan has duplicate identifiers
- **WHEN** a plan contains duplicate workspace aliases or duplicate card ids
- **THEN** `preflight-plan` records `BLOCKED` aggregate status and exits
  non-zero

#### Scenario: Concurrency settings conflict
- **WHEN** `max_parallel` is less than one or per-workspace parallelism allows
  more than one live card in a workspace
- **THEN** `preflight-plan` records `BLOCKED` aggregate status and exits
  non-zero

#### Scenario: Workspace readiness fails
- **WHEN** a workspace is missing, is not a git repository, lacks the configured
  single-card runner readiness, or has unsafe initial git/card state
- **THEN** `preflight-plan` records the failing check in aggregate status and
  exits non-zero

### Requirement: Stable queue card resolution
The delivery runner MUST resolve queue cards by stable filename or card id
across board lanes before listing, preflighting, running or resuming a plan.

#### Scenario: Card moved after plan was written
- **WHEN** a plan references a card filename that currently exists in exactly
  one board lane
- **THEN** the runner uses the current card path in the resolved plan

#### Scenario: Card is missing or duplicated
- **WHEN** a plan card cannot be found or resolves to more than one board path
- **THEN** the plan command fails closed before any child launch

#### Scenario: Card is canceled
- **WHEN** a plan card resolves under `openspec/board/5.canceled/`
- **THEN** the plan command fails closed unless an explicit future operator
  override is implemented and recorded

### Requirement: Queue preflight aggregate status
The delivery runner MUST write schema-backed aggregate status for plan preflight
and status inspection.

#### Scenario: Preflight succeeds
- **WHEN** `preflight-plan` validates every workspace, card and dependency
- **THEN** aggregate status records `DELIVERED` as the preflight result, the
  plan fingerprint and all resolved card states without child run references

#### Scenario: Operator reads status
- **WHEN** an operator invokes `status-plan` for a prior queue run or preflight
- **THEN** the command reads the aggregate status record and reports structured
  queue state without parsing raw child stdout or stderr

### Requirement: Live queue plan execution
The delivery runner MUST execute `run-plan` by launching the existing
single-card runner once for each live card that is ready by dependency and wave.

#### Scenario: Child card starts
- **WHEN** a card becomes runnable in `run-plan`
- **THEN** the queue runner invokes `bin/changerail-delivery-runner run <card>`
  for that card's resolved workspace
- **AND** the child writes a separate `changerail.delivery-run.v1` status record

#### Scenario: Queue preserves workspace serialization
- **WHEN** multiple runnable cards belong to the same workspace
- **THEN** at most one card from that workspace is live at a time

#### Scenario: Queue allows cross-workspace parallelism
- **WHEN** runnable cards belong to dependency-independent workspaces
- **THEN** the queue runner may run them in parallel up to `max_parallel`

### Requirement: Queue dependency and wave barriers
The delivery runner MUST enforce plan dependencies and wave barriers
deterministically during live and resumed queue execution.

#### Scenario: Dependency is incomplete
- **WHEN** a card depends on another card whose terminal outcome is not a
  successful queue outcome
- **THEN** the dependent card is not launched

#### Scenario: Wave barrier blocks downstream cards
- **WHEN** a later wave contains cards but an earlier wave has unfinished or
  failed cards
- **THEN** the later wave is not launched

### Requirement: Queue fail-fast terminal outcomes
The delivery runner MUST stop launching new downstream cards when a live child
or queue validation reaches an unsafe terminal outcome. Autonomous recovery
after child `NO-GO` MUST be represented as a linked rescue/replacement or
investigation card before dependent downstream cards resume.

#### Scenario: Child returns no-go
- **WHEN** a child delivery run returns `NO-GO`
- **THEN** aggregate queue status records `NO-GO`
- **AND** no new downstream cards are launched

#### Scenario: Autonomous recovery is represented as a card
- **WHEN** an autonomous agent continues after a terminal child `NO-GO`
- **THEN** it MUST create or run a linked rescue/replacement or investigation
  card rather than pushing the failed child payload
- **AND** the original aggregate plan may resume only after the recovery card
  publishes with a fresh independent `GO`

#### Scenario: Child returns blocked
- **WHEN** a child delivery run returns `BLOCKED`
- **THEN** aggregate queue status records `BLOCKED`
- **AND** no new downstream cards are launched

#### Scenario: Repository state is inconsistent after child success
- **WHEN** child status reports `DELIVERED` but card location, git cleanliness,
  upstream equality or no-push ahead-state success checks fail
- **THEN** aggregate queue status records `BLOCKED`

### Requirement: Queue workspace locks
The delivery runner MUST use ignored workspace locks to prevent concurrent live
queue children in the same repository.

#### Scenario: Workspace lock exists
- **WHEN** a queue attempts to launch a card in a workspace with an active lock
- **THEN** the launch is blocked with structured diagnostics

#### Scenario: Lock appears stale
- **WHEN** a workspace lock appears older than the current run
- **THEN** the runner reports stale-lock diagnostics
- **AND** it does not delete the lock automatically without an explicit safe
  operator action

### Requirement: Safe queue resume
The delivery runner MUST implement `resume-plan` without re-running already
successful queue cards and without trusting stale plan or repository state.

#### Scenario: Resume sees delivered card
- **WHEN** aggregate status shows a card succeeded and current workspace state
  still satisfies the selected push or no-push success criteria
- **THEN** `resume-plan` skips that card

#### Scenario: Resume sees moved unfinished card
- **WHEN** an unfinished card has moved to another non-canceled board lane
- **THEN** `resume-plan` re-resolves the current card path before launching it

#### Scenario: Plan fingerprint changed
- **WHEN** the current plan fingerprint differs from the aggregate status
  fingerprint
- **THEN** `resume-plan` records `BLOCKED` and exits non-zero before launching
  unfinished cards

### Requirement: Queue success criteria
The delivery runner MUST distinguish push-enabled and explicit `--no-push`
queue success criteria.

#### Scenario: Push-enabled card succeeds
- **WHEN** a child returns `DELIVERED` in push-enabled mode
- **THEN** queue success for that card requires exactly one card location under
  `openspec/board/4.done/`, a clean owning repository and `HEAD == upstream`

#### Scenario: No-push card succeeds
- **WHEN** a child returns `DELIVERED` in explicit `--no-push` mode
- **THEN** queue success for that card requires a committed clean tree and the
  expected ahead-of-upstream state recorded in aggregate status

### Requirement: Per-card queue overrides
The delivery runner MUST support per-card model and reasoning overrides from
the plan without changing repository defaults.

#### Scenario: Card override is declared
- **WHEN** a plan card declares model or reasoning effort
- **THEN** the corresponding single-card child invocation receives those
  overrides for that run only
