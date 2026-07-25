# changerail-project-verification Specification

## Purpose
Зафиксировать red/green gate, который проверяет, что consumer project
подключен к ChangeRail source of truth и имеет project-local config, OpenSpec
validation и runtime/auth ignore policy.
## Requirements
### Requirement: Consumer project verification gate
ChangeRail MUST provide `bin/verify-project <path>` as a red/green gate for consumer
project wiring and baseline configuration.

#### Scenario: Valid consumer project passes verification
- **WHEN** `bin/verify-project /opt/example-project` runs against a correctly
  wired consumer project
- **THEN** it exits `0` after checking symlink-и, configs, OpenSpec validation,
  helper/schema reachability and ignored runtime/auth paths

#### Scenario: Invalid consumer project fails verification
- **WHEN** required ChangeRail wiring, config or ignore policy is missing
- **THEN** `bin/verify-project` exits non-zero and reports the failed check

### Requirement: Полное покрытие ChangeRail contract schemas
`verify-project` и его smoke checks MUST валидировать reachability для каждой
public ChangeRail contract schema, tracked в source repository.

#### Scenario: Все public schemas существуют
- **WHEN** `bin/verify-project <path>` запускается для consumer project
- **THEN** он проверяет review verdict, review cycle history, delivery manifest,
  delivery run и evidence index schema files

#### Scenario: Public schema отсутствует
- **WHEN** любой public ChangeRail contract schema file отсутствует в
  ChangeRail source root
- **THEN** verification завершается non-zero и указывает missing schema

### Requirement: ChangeRail source resolution
Verification MUST accept ChangeRail-owned surfaces that resolve directly to
`/opt/changerail` or through an explicitly documented aggregator path.

#### Scenario: Consumer uses direct ChangeRail wiring
- **WHEN** a required symlink resolves under `/opt/changerail`
- **THEN** verification treats the path as valid ChangeRail source wiring

#### Scenario: Consumer uses aggregator wiring
- **WHEN** an operator passes `--aggregator-root <path>` and required symlink-и
  resolve through that root to ChangeRail-owned surfaces
- **THEN** verification treats the path as valid aggregator wiring

### Requirement: Project-local config gates
Verification MUST parse project-local `.mcp.json`, `.codex/config.toml` and
`openspec/config.yaml`.
Verification MUST validate that generated config scopes filesystem access and
trusted project settings to the consumer project by default.
Verification MUST fail closed when generated MCP config uses unpinned or
unlocked automatically executed npm package references.
Verification MUST compare tracked npm MCP integrity metadata with the npm
registry during trusted setup verification.

#### Scenario: Config scope is project-local
- **WHEN** verification inspects MCP and Codex config
- **THEN** filesystem scope and trust settings cover the consumer project root
  instead of the ChangeRail repository root

#### Scenario: Verifier checks MCP npm package pins
- **WHEN** `bin/verify-project <path>` inspects generated MCP config
- **THEN** it fails if an automatically executed npm MCP package is missing an
  exact version
- **AND** it fails if the package/version is absent from the tracked MCP npm
  integrity lock

#### Scenario: Verifier checks MCP npm integrity
- **WHEN** `bin/verify-project <path>` inspects generated MCP config in a
  trusted setup environment
- **THEN** it fails if tracked `mcp-npm-lock.json` integrity is not SRI-shaped
- **AND** it fails if `npm view <package>@<version> dist.integrity --json`
  returns different integrity for any referenced MCP package

### Requirement: Runtime/auth ignore policy
Verification MUST fail when consumer projects do not ignore ChangeRail runtime,
agent session and auth paths.

#### Scenario: Runtime path would be committed
- **WHEN** `.runtime/`, `.artifacts/`, `.ai/`, Codex runtime/auth state or
  Claude local settings are not ignored
- **THEN** `bin/verify-project` exits non-zero

#### Scenario: Supported auth marker is tracked
- **WHEN** a consumer project force-tracks `.codex/auth.json`,
  `.codex/auth.toml` or another supported Codex auth marker that belongs to
  local auth state
- **THEN** `bin/verify-project` exits non-zero
- **AND** it reports the tracked runtime/auth file as forbidden

### Requirement: Verify ChangeRail consumer wiring
`verify-project` MUST validate ChangeRail consumer wiring after the rename.

#### Scenario: Consumer is correctly wired
- **WHEN** `verify-project` runs for a generated ChangeRail consumer
- **THEN** `.claude/commands/changerail`, `.claude/skills`,
  `.codex/skills/changerail-*`, `bin/changerail-*` and `bin/openspec` resolve
  to the ChangeRail source of truth

#### Scenario: Consumer still uses stale OPSX wiring
- **WHEN** `verify-project` finds stale `.claude/commands/opsx`,
  `.codex/skills/opsx-*` or `bin/opsx-*` defaults
- **THEN** verification fails with a message identifying the stale wiring

### Requirement: Repository rename gate before known consumer migration
Known consumer migration MUST NOT start until the ChangeRail repository remote
has been updated after the GitHub repository rename.

#### Scenario: Repository remote still points to old OPSX URL
- **WHEN** delivery reaches known consumer migration and `git remote -v` still
  points at the old `opsx` repository URL
- **THEN** delivery stops before editing any consumer project
- **AND** it asks the operator to rename the GitHub repository to `changerail`
  and update or confirm local `origin`

#### Scenario: Repository remote points to ChangeRail URL
- **WHEN** delivery reaches known consumer migration and `git remote -v` points
  at the `changerail` repository URL
- **THEN** delivery may proceed to the one-project-at-a-time consumer migration
  protocol

### Requirement: Known consumer migration verification
Each known local consumer rewired by the operator MUST pass the post-rename
ChangeRail project verification gate before being treated as ChangeRail-wired.

#### Scenario: Consumer rewiring completes
- **WHEN** an operator finishes rewiring one selected consumer project
- **THEN** `/opt/changerail/bin/verify-project <project>` passes for that
  project
- **AND** the verification result is recorded in the consumer repository or
  ignored operator notes

#### Scenario: Active session cannot be stopped immediately
- **WHEN** a selected consumer cannot safely stop active Claude/Codex sessions
  during the main ChangeRail rename
- **THEN** the remaining restart and fresh-context verification work is tracked
  in a separate board card
- **AND** the consumer is not treated as ready for `/changerail:*` or
  `$changerail-*` use until that follow-up is complete

#### Scenario: Consumer has unrelated work in progress
- **WHEN** the selected consumer has unrelated dirty tracked files before
  migration
- **THEN** migration pauses for that project instead of mixing wiring changes
  with unrelated work

### Requirement: Verify short ChangeRail aliases
`verify-project` MUST validate short `chrl-*` ChangeRail alias wiring for
generated or migrated consumer projects.

#### Scenario: Consumer has complete short alias wiring
- **WHEN** `verify-project` runs for a correctly wired ChangeRail consumer
- **THEN** `.claude/commands/chrl` resolves to the ChangeRail source of truth
- **AND** `.codex/skills/chrl-*` resolves to tracked ChangeRail alias skill
  directories
- **AND** the consumer passes verification

#### Scenario: Consumer is missing a short alias
- **WHEN** a generated ChangeRail consumer is missing `.codex/skills/chrl-do`
  or `.claude/commands/chrl`
- **THEN** `verify-project` exits non-zero
- **AND** the output identifies the missing short alias wiring

### Requirement: Delivery runner auth readiness advisory
`verify-project` MUST report delivery runner Codex auth readiness as a
non-fatal advisory while preserving existing mandatory verification gates.

#### Scenario: Consumer has project-local auth marker
- **WHEN** `bin/verify-project /opt/example-project` finds a supported auth
  marker under `/opt/example-project/.codex`
- **THEN** verification reports a passing delivery runner auth readiness
  advisory
- **AND** it does not read or print credential contents

#### Scenario: Consumer relies on auth environment variable
- **WHEN** verification runs with a supported Codex auth environment variable
  set
- **THEN** verification reports a passing delivery runner auth readiness
  advisory
- **AND** it identifies the environment variable name without printing the
  value

#### Scenario: Consumer is missing delivery auth
- **WHEN** required ChangeRail wiring passes but no supported auth marker or
  environment variable is present
- **THEN** `verify-project` exits `0`
- **AND** it reports a warning advisory with the next remediation step for
  delivery runner readiness
