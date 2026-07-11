# opsx-skill-surface Specification

## Purpose
Зафиксировать минимальный public source surface для generic OPSX skills и
Claude command wrappers: какие skills поставляются первыми, какие boundaries у
planning-only flow и какие path-neutrality требования должны соблюдаться до
подключения bootstrap/adoption wiring.

## Requirements
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

### Requirement: Explore remains non-implementation mode
`opsx-explore` MUST describe an exploration workflow that reads relevant project
context and helps shape the problem without implementing product/runtime
changes.

#### Scenario: User invokes explore for an unclear requirement
- **WHEN** agent follows `opsx-explore`
- **THEN** agent investigates, compares options and recommends next artifacts
  without applying code changes

### Requirement: Fast-forward remains planning-only
`opsx-ff` MUST describe a card planning workflow that decomposes stories and
creates apply-ready OpenSpec artifacts without implementing, archiving or
publishing.

#### Scenario: User invokes fast-forward for a board card
- **WHEN** agent follows `opsx-ff`
- **THEN** agent updates the card and OpenSpec change artifacts while leaving
  implementation to a later delivery workflow

### Requirement: Claude wrappers for minimal commands
OPSX MUST provide Claude command wrapper source files for `/opsx:explore`,
`/opsx:ff`, `/opsx:do`, `/opsx:review`, `/opsx:pub` and `/opsx:deliver`.

#### Scenario: Consumer project wires Claude commands
- **WHEN** consumer project links `claude/commands/opsx/`
- **THEN** source wrappers exist for the generic OPSX lifecycle commands

### Requirement: Claude wrappers use skill discovery
Claude command wrappers MUST load OPSX skills by name or by the consumer's
Claude skill discovery mechanism, not by assuming a root-level `skills/` path in
the consumer repository.

#### Scenario: Consumer project links commands and skills through documented wiring
- **WHEN** consumer project exposes OPSX commands under `.claude/commands/opsx`
  and skills under `.claude/skills`
- **THEN** `/opsx:explore` and `/opsx:ff` do not require a separate
  `<consumer-root>/skills` symlink

### Requirement: Fast-forward handoff is conditional
`opsx-ff` MUST hand off to the delivery workflow without requiring `opsx-do` to
be installed by the minimal skill surface.

#### Scenario: Minimal skill surface is installed without delivery commands
- **WHEN** `opsx-ff` finishes planning a card
- **THEN** it may name `$opsx-do` or `/opsx:do` only as the delivery command to
  use when that surface is installed

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

### Requirement: Delivery skills preserve review-gated lifecycle
OPSX lifecycle skills MUST keep implementation, independent review and publish
as separate gates with explicit card-state responsibilities.

#### Scenario: Delivery hands off without done move
- **WHEN** `opsx-do` completes and archives all card-owned changes
- **THEN** it records verification and archive evidence but does not move the
  card to `4.done`

#### Scenario: Publish performs final board transition
- **WHEN** `opsx-pub` has a fresh valid `go` verdict and publishes the scoped
  payload
- **THEN** it performs only the documented board finalization needed to mark the
  story done

### Requirement: Delivery and review audit mandatory verification
`opsx-do` MUST collect mandatory verification from local rules and artifacts,
and `opsx-review` MUST audit whether mandatory verification claims are backed by
concrete evidence.

#### Scenario: Delivery hands off evidence
- **WHEN** `opsx-do` completes a change with mandatory checks
- **THEN** the card, tasks or delivery manifest contains command/outcome
  evidence for those checks

#### Scenario: Review finds an unbacked mandatory claim
- **WHEN** `opsx-review` sees a mandatory verification claim without concrete
  command/outcome evidence
- **THEN** it records a finding instead of treating the claim as proven
