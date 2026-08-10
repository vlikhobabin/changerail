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

### Requirement: Discovery smoke covers short aliases
Wiring discovery smoke MUST validate short `chrl-*` Codex skill aliases and
`/chrl:*` Claude command aliases alongside canonical ChangeRail lifecycle
names.

#### Scenario: Repo-local alias wiring is checked
- **WHEN** wiring smoke validates the ChangeRail repository
- **THEN** `.codex/skills/chrl-*` resolves to tracked ChangeRail alias skill
  directories
- **AND** `.claude/commands/chrl` resolves to the tracked short command wrapper
  directory

#### Scenario: Consumer-example alias wiring is checked
- **WHEN** wiring discovery smoke validates a generated consumer example
- **THEN** the consumer exposes `/chrl:*` Claude command aliases
- **AND** the consumer exposes `chrl-*` Codex skill aliases through symlinks to
  the ChangeRail source of truth

#### Scenario: Short alias is missing from smoke target
- **WHEN** a smoke target is missing a required `chrl-*` skill or `/chrl:*`
  command wrapper
- **THEN** wiring discovery smoke fails with a report entry identifying the
  missing alias

### Requirement: Wiring smoke parses complete skill frontmatter
Wiring discovery smoke MUST parse the full YAML frontmatter for every bundled
skill it validates, rather than extracting only the `name` line with string
splitting.

#### Scenario: Codex skill contract is checked
- **WHEN** wiring smoke validates a `skills/*/SKILL.md` file through repo-local
  or consumer-example Codex wiring
- **THEN** it parses the complete frontmatter as YAML
- **AND** it fails if any frontmatter field makes the YAML document invalid

#### Scenario: Claude skill contract is checked
- **WHEN** wiring smoke validates a bundled skill through Claude skill wiring
- **THEN** it uses the same complete YAML frontmatter parser as Codex skill
  checks
- **AND** it still verifies that parsed `name` matches the expected skill name

### Requirement: Wiring smoke rejects colon scalar regression
Wiring discovery smoke MUST include a deterministic negative fixture proving
that an unquoted scalar containing `: ` is rejected.

#### Scenario: Negative skill metadata fixture is parsed
- **WHEN** wiring smoke runs its frontmatter parser regression check
- **THEN** a fixture with `description: invalid: scalar` fails parsing
- **AND** the smoke fails if that fixture is accepted

### Requirement: Generated Windows wiring discovery
Wiring discovery MUST recognize generated project-local command, skill and
helper wiring as the native Windows default for generated consumers.

#### Scenario: Consumer uses generated Windows wiring
- **WHEN** wiring discovery or smoke validates a generated native Windows
  consumer
- **THEN** command, skill and helper surfaces may be generated project-local
  files or directories rather than symlinks
- **AND** the generated surfaces are accepted only when tracked ownership
  metadata identifies their ChangeRail source identity

#### Scenario: Generated surfaces are classified
- **WHEN** discovery reports generated Windows wiring
- **THEN** directory surfaces and file surfaces are classified separately
- **AND** the report distinguishes generated-copy wiring from symlink and
  junction fallback modes

### Requirement: POSIX discovery compatibility
Wiring discovery MUST preserve existing POSIX symlink discovery behavior while
adding generated Windows wiring.

#### Scenario: POSIX consumer uses symlink wiring
- **WHEN** wiring discovery validates an existing POSIX-generated consumer
- **THEN** symlink-based `.claude`, `.codex` and `bin/` wiring continues to pass
- **AND** generated Windows wiring checks do not require POSIX consumers to copy
  ChangeRail-owned surfaces

### Requirement: Generated wiring drift and refresh discovery
Wiring discovery MUST expose whether generated Windows wiring is fresh, stale,
project-owned or using an explicit fallback mode.

#### Scenario: Discovery reports generated wiring freshness
- **WHEN** wiring discovery validates a generated Windows consumer
- **THEN** it reports generated-owned artifacts as fresh only when source
  identity and digest match the ChangeRail source of truth
- **AND** stale generated artifacts are reported with a refresh remediation

#### Scenario: Discovery reports fallback mode
- **WHEN** a Windows consumer uses symlink or junction fallback wiring
- **THEN** discovery reports the fallback mode separately from generated-copy
  wiring
- **AND** it identifies the source metadata and concrete per-check evidence
  required for that fallback to pass

### Requirement: Generated wiring freshness diagnostics
Wiring discovery diagnostics consumed by verification and drift gates MUST
distinguish fresh, stale, missing and project-owned generated Windows wiring.

#### Scenario: Generated wiring diagnostics are fresh
- **WHEN** a generated Windows consumer has manifest-owned artifacts that match
  the ChangeRail source identity and digest
- **THEN** diagnostics identify the generated-copy mode as fresh

#### Scenario: Generated wiring diagnostics are stale or missing
- **WHEN** a generated Windows consumer has stale or missing manifest-owned
  artifacts
- **THEN** diagnostics identify the affected project-relative path
- **AND** diagnostics include a refresh remediation without copying raw source
  content into tracked output

#### Scenario: Generated wiring diagnostics see project-owned content
- **WHEN** a generated Windows wiring destination contains project-owned content
  or lacks generated ownership metadata
- **THEN** diagnostics identify project-owned divergence separately from stale
  generated-copy drift

### Requirement: Lock-aware POSIX wiring discovery
Wiring discovery MUST classify POSIX symlink backend, absolute/relative path
mode, consumer-lock state and source match without exposing resolved machine
paths in tracked or public output.

#### Scenario: Absolute locked consumer is inspected
- **WHEN** discovery inspects a valid absolute POSIX consumer lock
- **THEN** it reports backend `symlink`, path mode `absolute`, lock enforcement
  and source-match status
- **AND** public output does not include the resolved root

#### Scenario: Relative locked consumer is inspected
- **WHEN** discovery inspects an explicitly relative consumer
- **THEN** it reports path mode `relative` and the required shared-tree topology

#### Scenario: Lock and actual wiring disagree
- **WHEN** actual symlink targets contradict declared path mode or artifact intent
- **THEN** discovery reports broken wiring rather than normal source drift

### Requirement: POSIX clean-clone discovery evidence
ChangeRail MUST provide a regression fixture that commits a POSIX consumer,
clones it into a non-sibling path, performs lock-driven repair when needed and
then runs discovery and verification.

#### Scenario: Consumer checkout topology changes
- **WHEN** the clean-clone fixture moves only the consumer checkout
- **THEN** the documented absolute contract or lock-driven repair restores valid
  discovery without manual symlink edits
