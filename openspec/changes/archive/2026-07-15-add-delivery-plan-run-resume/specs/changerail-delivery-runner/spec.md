## ADDED Requirements

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
or queue validation reaches an unsafe terminal outcome.

#### Scenario: Child returns no-go
- **WHEN** a child delivery run returns `NO-GO`
- **THEN** aggregate queue status records `NO-GO`
- **AND** no new downstream cards are launched

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
