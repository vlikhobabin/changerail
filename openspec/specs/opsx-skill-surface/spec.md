# opsx-skill-surface Specification

## Purpose
Зафиксировать минимальный public source surface для generic OPSX skills и
Claude command wrappers: какие skills поставляются первыми, какие boundaries у
planning-only flow и какие path-neutrality требования должны соблюдаться до
подключения bootstrap/adoption wiring.

## Requirements
### Requirement: Minimal generic OPSX skills
OPSX MUST provide tracked generic source skills for `opsx-explore` and
`opsx-ff`.

#### Scenario: Consumer project links minimal OPSX skills
- **WHEN** consumer project symlinks or copies OPSX skill source files
- **THEN** `opsx-explore` and `opsx-ff` are available from `skills/`

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
OPSX MUST provide Claude command wrapper source files for `/opsx:explore` and
`/opsx:ff`.

#### Scenario: Consumer project wires Claude commands
- **WHEN** consumer project links `claude/commands/opsx/`
- **THEN** source wrappers exist for explore and fast-forward planning commands

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
