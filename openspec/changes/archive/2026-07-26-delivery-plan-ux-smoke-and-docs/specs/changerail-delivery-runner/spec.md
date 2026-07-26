## MODIFIED Requirements

### Requirement: Plan-oriented dry-run commands
The delivery runner MUST provide explicit plan-oriented commands that resolve a
queue plan without launching live child deliveries, and its smoke coverage MUST
prove generated plan examples can be inspected before live delivery.

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

#### Scenario: Generated example validates before live delivery
- **WHEN** smoke coverage generates a representative delivery plan
- **THEN** the generated file validates through `plan` and `preflight-plan`
- **AND** the smoke does not launch live child delivery

### Requirement: Queue preflight aggregate status
The delivery runner MUST write schema-backed aggregate status for plan preflight
and status inspection, with smoke coverage for compact child diagnostics.

#### Scenario: Preflight succeeds
- **WHEN** `preflight-plan` validates every workspace, card and dependency
- **THEN** aggregate status records `DELIVERED` as the preflight result, the
  plan fingerprint and all resolved card states without child run references

#### Scenario: Operator reads status
- **WHEN** an operator invokes `status-plan` for a prior queue run or preflight
- **THEN** the command reads the aggregate status record and reports structured
  queue state without parsing raw child stdout or stderr

#### Scenario: Smoke covers compact child diagnostics
- **WHEN** smoke coverage simulates a child preflight check failure
- **THEN** it asserts compact aggregate output and schema-valid status without
  raw child stdout or stderr logs

### Requirement: Consumer Codex auth setup documentation
ChangeRail runner documentation MUST describe queue launcher semantics and MUST
avoid implying tracked consumer repo-local Codex launchers are mandatory.

#### Scenario: Docs smoke checks launcher semantics
- **WHEN** smoke coverage inspects durable runner docs
- **THEN** it finds wording that distinguishes plan runner, single-card runner
  and Codex launcher
- **AND** it finds wording that describes a supported path when a consumer
  repo-local `bin/codex` is absent or optional
