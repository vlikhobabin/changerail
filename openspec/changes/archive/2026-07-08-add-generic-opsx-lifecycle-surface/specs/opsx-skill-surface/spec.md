## MODIFIED Requirements

### Requirement: Minimal generic OPSX skills
OPSX MUST provide tracked generic source skills for `opsx-explore`, `opsx-ff`,
`opsx-do`, `opsx-review`, `opsx-pub` and `opsx-deliver`.

#### Scenario: Consumer project links OPSX lifecycle skills
- **WHEN** consumer project symlinks or copies OPSX skill source files
- **THEN** all generic OPSX lifecycle skills are available from `skills/`

### Requirement: Path-neutral skill content
OPSX skill source files MUST avoid private workspace names, machine-specific
fallback paths, customer data, secrets and domain-specific provider policy.

#### Scenario: Public-surface scan runs before publication
- **WHEN** skill files are scanned for private local paths and workspace names
- **THEN** no private machine-local source path appears in the generic skill
  surface

### Requirement: Claude wrappers for minimal commands
OPSX MUST provide Claude command wrapper source files for `/opsx:explore`,
`/opsx:ff`, `/opsx:do`, `/opsx:review`, `/opsx:pub` and `/opsx:deliver`.

#### Scenario: Consumer project wires Claude commands
- **WHEN** consumer project links `claude/commands/opsx/`
- **THEN** source wrappers exist for the generic OPSX lifecycle commands

## ADDED Requirements

### Requirement: Delivery skill implements generic do flow
`opsx-do` MUST describe a supervised delivery workflow that implements ordered
card-owned OpenSpec changes, verifies them, syncs specs and archives completed
changes without committing or publishing.

#### Scenario: Agent invokes delivery for a planned card
- **WHEN** agent follows `opsx-do` for a card with apply-ready changes
- **THEN** the agent processes each card-owned change through implementation,
  verification, spec sync and archive before handing off to review

### Requirement: Review skill enforces independent gate
`opsx-review` MUST require a fresh context that did not plan or implement the
card and MUST write only an ignored runtime verdict file.

#### Scenario: Implementing session attempts self-review
- **WHEN** the current session produced the diff under review
- **THEN** `opsx-review` stops before writing a verdict

### Requirement: Publish skill requires review gate by default
`opsx-pub` MUST fail closed for review-gated cards when a fresh valid `go`
verdict is absent or stale.

#### Scenario: Publish runs without a valid review verdict
- **WHEN** publish is invoked for a delivered card without a fresh `go` verdict
- **THEN** publish stops before staging, committing or pushing files

### Requirement: Deliver skill orchestrates the lifecycle
`opsx-deliver` MUST orchestrate the card-level flow `ff -> do -> review -> pub`
while preserving phase safety stops and scoped publish behavior.

#### Scenario: Deliver reaches an external review stop
- **WHEN** an operator requires external review instead of self-launched review
- **THEN** `opsx-deliver` stops at the review gate and prints the review and
  resume commands without publishing
