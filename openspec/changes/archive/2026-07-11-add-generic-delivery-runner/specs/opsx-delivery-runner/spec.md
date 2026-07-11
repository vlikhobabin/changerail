## ADDED Requirements

### Requirement: Non-interactive delivery runner
OPSX MUST provide a tracked generic helper that can launch a non-interactive
delivery run for a single board card without private workspace assumptions.

#### Scenario: Runner starts a card delivery
- **WHEN** an operator invokes the runner with a card path
- **THEN** the helper launches Codex non-interactively with instructions to run
  `$opsx-deliver <card-path>` for that card
- **AND** when `--workspace` is omitted, the requested workspace resolves to
  the invocation repository root, or the current working directory outside git
- **AND** the child process runs with cwd and `CODEX_WORKDIR` set to the
  requested workspace
- **AND** absent an explicit operator `CODEX_HOME`, the child uses
  `<workspace>/.codex`

### Requirement: Closed stdin execution
The runner MUST close stdin for the child process it launches.

#### Scenario: Runner runs in background
- **WHEN** the helper starts `codex exec`
- **THEN** the child receives closed or null stdin and cannot block waiting for
  inherited terminal input

### Requirement: Per-run Codex overrides
The runner MUST support per-run `model` and `reasoning_effort` overrides using
standard Codex CLI options while preserving existing defaults when overrides are
absent.

#### Scenario: Operator sets model and effort
- **WHEN** the operator passes model and reasoning effort options
- **THEN** the child Codex command includes those overrides for that run only

#### Scenario: Operator omits overrides
- **WHEN** the operator passes no model or reasoning effort
- **THEN** the runner does not modify repository default model configuration

### Requirement: Structured runtime status
The runner MUST atomically write a machine-readable runtime status or run record
with card, phase, result, timestamps, terminal outcome and commit when
available.

#### Scenario: Supervisor polls status
- **WHEN** a delivery run starts, changes phase or terminates
- **THEN** `<workspace>/.runtime/opsx/delivery-runs/<run-id>/status.json`
  contains the latest structured state without requiring log scraping unless
  `--runtime-root` is explicitly supplied
- **AND** the record contains the workspace `HEAD` as `commit` when available

### Requirement: Explicit terminal outcomes
The runner MUST report terminal outcomes `DELIVERED`, `NO-GO` and `BLOCKED`
without relying on free-text log interpretation.

#### Scenario: Codex exits successfully
- **WHEN** the non-interactive delivery command exits `0`
- **THEN** the runner records `DELIVERED`

#### Scenario: Codex exits unsuccessfully
- **WHEN** the non-interactive delivery command exits non-zero
- **THEN** the runner records `BLOCKED` unless structured output identifies
  the result as `NO-GO`

#### Scenario: Structured review event returns no-go
- **WHEN** Codex JSONL contains a structured event such as
  `external-review/no-go`
- **THEN** the runner records and prints terminal outcome `NO-GO`

#### Scenario: Structured review stop awaits external review
- **WHEN** Codex JSONL contains a structured `awaiting-review` event
- **THEN** the runner records and prints terminal outcome `BLOCKED`

#### Scenario: Command run preflight fails
- **WHEN** delivery `run` preflight checks fail before launching Codex
- **THEN** the runner records and prints terminal outcome `BLOCKED`

### Requirement: Delivery runner preflight
The runner MUST provide a preflight mode that checks the Codex launcher,
effective `CODEX_HOME`, auth state, `CODEX_HOME` config, stale symlinks,
executable permissions and optional connectivity URL.

#### Scenario: Connectivity check is requested
- **WHEN** an operator supplies a connectivity URL for preflight
- **THEN** the runner performs an actual connection attempt and records pass or
  fail in structured output

#### Scenario: Auth or wiring is stale
- **WHEN** auth markers are absent or `CODEX_HOME` contains broken symlinks
- **THEN** preflight records explicit diagnostics before the delivery child is
  launched
