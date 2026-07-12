# changerail-project-bootstrap Specification

## Purpose
Зафиксировать command-line bootstrap flow, который создает generic ChangeRail
consumer project из tracked templates, ChangeRail source-of-truth symlink-ов и
немедленно проверяет результат через `verify-project`.
## Requirements
### Requirement: Bootstrap project command
ChangeRail MUST provide `bin/bootstrap-project` to create a new generic consumer
project from tracked templates and ChangeRail source-of-truth symlink-и.
Bootstrap MUST generate public-safe portable tracked configuration by default
and expose local absolute-path configuration only through explicit operator
opt-in.

#### Scenario: Operator bootstraps a generic project
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the target receives generated project files, ChangeRail symlink-и, helper
  wrappers and an OpenSpec skeleton

#### Scenario: Default bootstrap creates portable tracked config
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the generated tracked files use portable project scope instead of a
  machine-local absolute target path
- **AND** bootstrap still creates the required ChangeRail symlinks and helper
  wrappers

#### Scenario: Operator explicitly opts into local config
- **WHEN** an operator runs bootstrap with local absolute config mode
- **THEN** bootstrap renders machine-local absolute paths only after explicit
  opt-in
- **AND** it prints a warning before the suggested `git add` command

### Requirement: Refuse existing targets by default
Bootstrap MUST refuse to overwrite an existing non-empty target unless the
operator explicitly requests backup mode.

#### Scenario: Target already contains files
- **WHEN** bootstrap is run for a non-empty existing target without
  `--backup-existing`
- **THEN** bootstrap exits non-zero before changing the target

### Requirement: Dry-run mode
Bootstrap MUST support a dry-run mode that reports planned operations without
creating or modifying the target project.

#### Scenario: Operator previews bootstrap
- **WHEN** bootstrap is run with `--dry-run`
- **THEN** planned file, directory and symlink actions are printed and the
  target project is not created

### Requirement: Bootstrap verification handoff
Bootstrap MUST run `verify-project` after generating a project unless the
operator explicitly skips verification for diagnostics.
Bootstrap verification MUST validate the config model produced by bootstrap
before reporting success.

#### Scenario: Generated project is verified
- **WHEN** bootstrap completes project generation
- **THEN** it runs `bin/verify-project <target>` and fails if verification
  fails

#### Scenario: Portable generated project is verified
- **WHEN** bootstrap completes default portable project generation
- **THEN** it runs `bin/verify-project <target>` and fails if portable scope
  validation fails

### Requirement: Bootstrap smoke evidence
ChangeRail MUST provide smoke coverage that exercises bootstrap end-to-end under
ignored runtime space.

#### Scenario: Bootstrap smoke runs
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it creates a temporary consumer under `.runtime`, verifies it and
  writes any report under ignored runtime space

### Requirement: Bootstrap creates ChangeRail consumers
Bootstrap MUST generate new generic consumers wired to the ChangeRail source of
truth.

#### Scenario: Operator bootstraps a post-rename project
- **WHEN** an operator runs bootstrap with `/opt/changerail` as the source of
  truth
- **THEN** the generated project uses `/opt/changerail` in generated docs and
  config
- **AND** generated helper symlinks point to ChangeRail helper wrappers

#### Scenario: Existing target is non-empty
- **WHEN** bootstrap is run for a non-empty existing target
- **THEN** bootstrap continues to refuse overwrite unless explicit backup mode
  is requested

### Requirement: Bootstrap installs short ChangeRail aliases
Bootstrap MUST generate new consumer projects with both canonical
`changerail-*` wiring and short `chrl-*` wiring for ChangeRail lifecycle
commands.

#### Scenario: Operator bootstraps a project with alias wiring
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the target receives `.codex/skills/chrl-*` entries for all generic
  ChangeRail lifecycle skills
- **AND** the target receives `.claude/commands/chrl` for all generic
  ChangeRail lifecycle commands
- **AND** canonical `changerail-*` wiring remains present

#### Scenario: Bootstrap dry-run reports alias wiring
- **WHEN** bootstrap is run with `--dry-run`
- **THEN** the planned operations include the short `chrl-*` Codex skill
  entries and `/chrl:*` Claude command directory

### Requirement: Bootstrap smoke checks workflow guidance
Bootstrap smoke MUST verify that generated consumer files include current
ChangeRail workflow guidance.

#### Scenario: Bootstrap smoke renders a generic consumer
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it checks generated `AGENTS.md` and `openspec/board/README.md`
- **AND** it fails if lifecycle, role model, fresh review gate or board
  finalization guidance is missing
