## MODIFIED Requirements

### Requirement: Non-interactive delivery runner
ChangeRail MUST provide a tracked generic helper that can launch a non-interactive
delivery run for a single board card without private workspace assumptions.

#### Scenario: Runner starts a card delivery
- **WHEN** an operator invokes the runner with a card path
- **THEN** the helper launches Codex non-interactively with instructions to run
  `$changerail-deliver <card-path>` for that card
- **AND** when `--workspace` is omitted, the requested workspace resolves to
  the invocation repository root, or the current working directory outside git
- **AND** the child process runs with cwd and `CODEX_WORKDIR` set to the
  requested workspace
- **AND** absent an explicit operator `CODEX_HOME`, the child uses
  `<workspace>/.runtime/changerail/codex-home`
- **AND** the child receives `CHANGERAIL_ACTIVE_RUN_ID` and
  `CHANGERAIL_ACTIVE_RUN_DIR` identifying parent-owned active runtime evidence

#### Scenario: Child explores delivery context
- **WHEN** a runner-launched child searches the workspace during delivery
- **THEN** the active runner directory is identifiable and excluded from child
  reads
- **AND** the child cannot recursively ingest its own growing JSONL log as
  task context

### Requirement: Delivery runner preflight
The runner MUST provide a preflight mode that checks the Codex launcher,
effective `CODEX_HOME`, auth state, effective project policy, stale symlinks,
executable permissions and optional connectivity URL.
Delivery runner preflight MUST sanitize connectivity diagnostics before writing
structured runtime status.

The runner MUST fail closed before launching a delivery child unless the
effective project policy grants unattended mutation authority with
`approval_policy = "never"` and `sandbox_mode = "danger-full-access"`.

#### Scenario: Effective Codex authority is insufficient
- **WHEN** preflight reads an effective Codex project config with missing or
  different approval/sandbox values
- **THEN** preflight reports a blocking `Codex automation authority` check
- **AND** no delivery child is launched

#### Scenario: Connectivity check is requested
- **WHEN** an operator supplies a connectivity URL for preflight
- **THEN** the runner performs an actual connection attempt and records pass or
  fail in structured output

#### Scenario: Auth or wiring is stale
- **WHEN** auth markers are absent or the effective runtime/project Codex layers
  contain broken symlinks
- **THEN** preflight records explicit diagnostics before the delivery child is
  launched

#### Scenario: Connectivity success is sanitized
- **WHEN** an operator supplies a connectivity URL containing URL userinfo or
  token-like query values and the request succeeds
- **THEN** the structured preflight check records only sanitized endpoint
  metadata and response status
- **AND** it does not include the raw submitted URL, userinfo or query value

#### Scenario: Connectivity failure is sanitized
- **WHEN** an operator supplies a connectivity URL containing URL userinfo or
  token-like query values and the request fails
- **THEN** the structured preflight check records sanitized endpoint metadata
  and the exception class
- **AND** it does not include the raw submitted URL or raw exception text

### Requirement: Consumer Codex auth setup documentation
ChangeRail runner documentation MUST describe the Codex auth prerequisite and
launcher semantics for single-card and plan-oriented delivery runner commands
without making credentials or repo-local launcher wrappers part of the tracked
consumer repository surface.

#### Scenario: Operator reads runner auth setup
- **WHEN** an operator reads the delivery runner or consumer adoption docs
- **THEN** the docs explain that `run`, `preflight-plan`, `run-plan` and
  `resume-plan` require an effective Codex auth source before unattended
  delivery can launch
- **AND** the docs describe the default ignored
  `<workspace>/.runtime/changerail/codex-home`, tracked project config and
  explicit `CODEX_HOME` override behavior

#### Scenario: Documentation gives safe remediation examples
- **WHEN** the docs describe missing-auth remediation
- **THEN** examples use generic paths such as `/opt/example-project` and
  `$HOME`
- **AND** examples include a project-local ignored auth marker symlink and an
  explicit `CODEX_HOME` invocation
- **AND** the docs do not instruct operators to commit credentials or runtime
  auth state

#### Scenario: Queue launcher chain is documented
- **WHEN** docs describe queue-plan execution
- **THEN** they distinguish the aggregate plan runner, the ChangeRail
  single-card runner child and the final Codex launcher invocation
- **AND** they state that `CODEX_WORKDIR` and the effective `CODEX_HOME` select
  the consumer workspace for each child run

#### Scenario: Repo-local Codex launcher is optional
- **WHEN** docs mention `bin/codex` for consumer repositories
- **THEN** they do not imply every consumer must track that file
- **AND** they describe the supported invocation path when a consumer repo-local
  launcher is absent

## ADDED Requirements

### Requirement: Default Codex runtime home isolation
The delivery runner MUST keep mutable Codex user state separate from tracked
project configuration for every invocation that does not explicitly set
`CODEX_HOME`.

#### Scenario: Default runtime home is prepared
- **WHEN** preflight runs without an explicit operator `CODEX_HOME`
- **THEN** the runner prepares a private ignored runtime home under
  `<workspace>/.runtime/changerail/codex-home`
- **AND** its user config binds exact absolute trust to the selected workspace
- **AND** unattended authority is validated from tracked
  `<workspace>/.codex/config.toml`

#### Scenario: Codex persists workspace trust
- **WHEN** a delivery child persists an absolute workspace trust entry into its
  user-level `CODEX_HOME/config.toml`
- **THEN** tracked `<workspace>/.codex/config.toml` remains byte-identical
- **AND** the persisted machine-local path remains ignored runtime state
- **AND** the persistence cannot add an unrelated path to the review payload

#### Scenario: Project auth marker is reused
- **WHEN** a supported ignored auth marker exists under project `.codex/` and no
  supported auth environment variable is set
- **THEN** the generated runtime home references that marker without reading or
  copying credential contents
- **AND** missing or stale auth still blocks child launch

#### Scenario: Explicit Codex home remains operator-owned
- **WHEN** an operator explicitly sets `CODEX_HOME`
- **THEN** the runner uses that home for config, authority, auth and symlink
  checks
- **AND** it does not generate or reconcile files in that operator-owned home

#### Scenario: Project skill link is stale
- **WHEN** the generated runtime home is valid but a symlink under project
  `.codex/skills/` is stale
- **THEN** preflight fails before child launch with sanitized wiring diagnostics

#### Scenario: Runtime home directory aliases another location
- **WHEN** any directory in the runner-owned default runtime-home chain is a
  symlink
- **THEN** preflight fails before chmod, file reconciliation or child launch
- **AND** tracked project configuration remains byte-identical
