# changerail-wiring-discovery Specification

## Purpose
Зафиксировать проверяемый wiring/discovery contract для подключения ChangeRail
skills и Claude command wrappers в проектах-потребителях и в repo-local
dogfooding `/opt/changerail`.
## Requirements
### Requirement: Consumer wiring contract
ChangeRail MUST define how consumer projects expose ChangeRail skills, OpenSpec lifecycle
skills, command wrappers and helper wrappers without requiring undocumented
root paths.

#### Scenario: Consumer project wires Claude surface
- **WHEN** a consumer project follows ChangeRail wiring
- **THEN** Claude commands resolve from `.claude/commands/changerail` and skills
  resolve from `.claude/skills`

#### Scenario: Consumer project wires Codex surface
- **WHEN** a consumer project follows ChangeRail wiring
- **THEN** Codex skills resolve from `.codex/skills/changerail-*` and
  `.codex/skills/openspec-*` entries without committing Codex runtime state

#### Scenario: Consumer project wires OpenSpec wrapper
- **WHEN** a consumer project follows ChangeRail wiring
- **THEN** `bin/openspec` can resolve to the ChangeRail wrapper while project-local
  OpenSpec artifacts remain in the consumer repository

### Requirement: Repo-local dogfooding wiring
ChangeRail MUST define repo-local dogfooding wiring for `/opt/changerail` without symlinks
to private workspaces.

#### Scenario: ChangeRail repository enables its own minimal surface
- **WHEN** `/opt/changerail` enables local discovery for ChangeRail skills or commands
- **THEN** public tracked files contain only relative links, generated wiring or
  documented generic `/opt/changerail` references

### Requirement: Discovery smoke evidence
ChangeRail MUST require smoke evidence that `changerail-explore` and `changerail-ff` are
discoverable through the documented Claude and Codex wiring surfaces.

#### Scenario: Discovery smoke runs for minimal ChangeRail surface
- **WHEN** wiring smoke is executed
- **THEN** a JSON report is written under ignored runtime space with schema
  `changerail.wiring-discovery-smoke.v1`
- **AND** the report records aggregate `runs[]` for repo-local and
  consumer-example checks across Claude command/skill discovery and Codex skill
  discovery
- **AND** each check records name, path, expected target, resolved target,
  status, message, mode and surface

### Requirement: Smoke pass criteria
ChangeRail MUST define deterministic pass/fail criteria for wiring discovery smoke.

#### Scenario: Smoke evaluates Claude wiring
- **WHEN** Claude wiring smoke runs
- **THEN** `.claude/skills` and `.claude/commands/changerail` resolve to the expected
  ChangeRail source directories
- **AND** `/changerail:explore` and `/changerail:ff` wrappers do not require a consumer-root
  `skills/` path

#### Scenario: Smoke evaluates Codex wiring
- **WHEN** Codex wiring smoke runs
- **THEN** `.codex/skills/changerail-explore` and `.codex/skills/changerail-ff` resolve to
  the expected ChangeRail source directories
- **AND** each resolved skill has a `SKILL.md` with matching frontmatter `name`

### Requirement: Public-safe wiring artifacts
ChangeRail wiring docs and smoke artifacts committed to the repository MUST avoid
private workspace names, machine-specific paths, secrets, local settings and
runtime state.

#### Scenario: Public-surface scan runs for wiring changes
- **WHEN** wiring docs or smoke scripts are prepared for commit
- **THEN** scan output contains no private workspace names or local-only state

### Requirement: ChangeRail command discovery wiring
Wiring discovery MUST verify ChangeRail lifecycle skills and Claude command
wrappers instead of OPSX lifecycle names.

#### Scenario: Repo-local wiring is checked
- **WHEN** wiring smoke validates the ChangeRail repository
- **THEN** `.claude/commands/changerail` resolves to the tracked ChangeRail
  command wrapper directory
- **AND** `.codex/skills/changerail-*` resolves to tracked ChangeRail lifecycle
  skill directories

#### Scenario: Consumer wiring is checked
- **WHEN** wiring smoke validates a generated consumer example
- **THEN** the consumer exposes `/changerail:*` Claude commands
- **AND** the consumer exposes `changerail-*` Codex skills through symlinks to
  the ChangeRail source of truth

### Requirement: Consumer-example smoke uses ChangeRail
Wiring discovery smoke MUST create and validate generated consumer examples
with ChangeRail command and skill names.

#### Scenario: Consumer example is created
- **WHEN** wiring discovery smoke runs in consumer-example mode
- **THEN** the temporary consumer exposes `.claude/commands/changerail`
- **AND** it exposes `.codex/skills/changerail-*` for generic lifecycle skills

#### Scenario: Stale command wrapper is present
- **WHEN** the generated consumer contains `.claude/commands/opsx`
- **THEN** wiring discovery smoke fails

### Requirement: Migrated consumers remove stale OPSX wiring
Known consumers migrated to ChangeRail MUST remove stale OPSX generic lifecycle
wiring from project-local discovery paths.

#### Scenario: Consumer is inspected after migration
- **WHEN** a migrated consumer's `.claude`, `.codex` and `bin` wiring is
  inspected
- **THEN** generic lifecycle wiring points to `/opt/changerail`
- **AND** stale `.claude/commands/opsx`, `.codex/skills/opsx-*` and
  `bin/opsx-*` defaults are absent unless explicitly retained as
  project-local legacy notes outside the generated ChangeRail surface

#### Scenario: Agent sessions resume
- **WHEN** migration verification passes for a consumer project
- **THEN** Claude/Codex sessions for that project are restarted, or an explicit
  follow-up card is recorded, before using `/changerail:*` or `$changerail-*`
