## ADDED Requirements

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
