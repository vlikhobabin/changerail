# changerail-delivery-runner Specification

## Purpose
Зафиксировать tracked generic runner для non-interactive ChangeRail delivery,
structured runtime status и operational preflight behavior.
## Requirements
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
  `<workspace>/.codex`
- **AND** the child receives `CHANGERAIL_ACTIVE_RUN_ID` and
  `CHANGERAIL_ACTIVE_RUN_DIR` identifying parent-owned active runtime evidence

#### Scenario: Child explores delivery context
- **WHEN** a runner-launched child searches the workspace during delivery
- **THEN** the active runner directory is identifiable and excluded from child
  reads
- **AND** the child cannot recursively ingest its own growing JSONL log as
  task context

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
- **THEN** `<workspace>/.runtime/changerail/delivery-runs/<run-id>/status.json`
  contains the latest structured state without requiring log scraping unless
  `--runtime-root` is explicitly supplied
- **AND** the record contains the workspace `HEAD` as `commit` when available

### Requirement: Structured live delivery progress
Delivery runner MUST publish optional `changerail.delivery-progress.v1` for a
running single-card child based on validated lifecycle events and bounded
activity heartbeat. Runner MUST NOT derive lifecycle transition from free-form
prose, command text or output.

#### Scenario: Lifecycle transition updates running status
- **WHEN** a matching child sends a schema-valid progress event for major
  transition `ff`, `do`, `review` or `publish`
- **THEN** runner atomically updates `progress.phase`, `progress.stage`,
  `heartbeat_at` and monotonic `event_counter`
- **AND** existing semantics `phase: delivery` and `result: RUNNING` do not
  change

#### Scenario: Untrusted content is not progress
- **WHEN** child prose, shell command or command output contains text that looks
  like a lifecycle phase or a synthetic private value
- **THEN** runner does not copy that value into progress
- **AND** phase/stage can change only through validated value-free lifecycle
  event

### Requirement: Stale heartbeat is a non-terminal diagnostic
Delivery runner MUST evaluate heartbeat age with observed process state and
MUST NOT terminate or classify a live child only because one heartbeat interval
was missed.

#### Scenario: Live child misses heartbeat interval
- **WHEN** heartbeat age exceeds documented stale threshold and child process
  remains alive
- **THEN** status reports bounded health `stale` and heartbeat age
- **AND** terminal outcome remains unset until existing terminal evidence
  appears

#### Scenario: Child terminates after stale heartbeat
- **WHEN** process exits after heartbeat became stale
- **THEN** runner determines terminal result through the existing terminal
  protocol
- **AND** progress health may report termination without replacing result

### Requirement: Single-card runtime status reader
The delivery runner MUST provide a read-only single-card status command that
inspects an existing `changerail.delivery-run.v1` record without launching,
resuming, stopping or mutating delivery state.

#### Scenario: Operator reads explicit single-card status
- **WHEN** an operator invokes
  `bin/changerail-delivery-runner status <status.json>`
- **THEN** the command validates the selected record as
  `changerail.delivery-run.v1`
- **AND** it prints compact human-readable fields for card, phase, result,
  `updated_at`, progress/health when present, `terminal_reason` when present
  and the selected status path
- **AND** it does not modify board files, process state, locks, manifests,
  verdicts, evidence indexes, logs or status records

#### Scenario: Operator selects status by run id
- **WHEN** an operator invokes
  `bin/changerail-delivery-runner status --run-id <run-id>`
- **THEN** the command resolves
  `.runtime/changerail/delivery-runs/<run-id>/status.json` under the effective
  workspace or explicit runtime root
- **AND** it validates and displays that exact record

#### Scenario: Operator reads latest workspace status
- **WHEN** an operator invokes `bin/changerail-delivery-runner status` without
  an explicit path or run id
- **THEN** the command selects the latest single-card status record from the
  effective workspace runtime root
- **AND** it fails closed when no status record exists

### Requirement: Status reader fails closed on invalid input
The single-card status reader MUST reject missing, corrupt, schema-invalid or
unsupported delivery-run records before displaying attention guidance.

#### Scenario: Explicit corrupt status is rejected
- **WHEN** the selected status path is missing, not JSON, not an object or fails
  `schemas/changerail-delivery-run.schema.json`
- **THEN** the status command exits non-zero
- **AND** it reports a concise diagnostic without falling back to another run

#### Scenario: Conflicting selectors are rejected
- **WHEN** an operator supplies more than one status selector, such as both an
  explicit path and `--run-id`
- **THEN** the command exits non-zero
- **AND** it does not choose a status record implicitly

#### Scenario: JSON mode returns the source record
- **WHEN** an operator invokes `bin/changerail-delivery-runner status --json`
  for a valid selected record
- **THEN** the command emits the schema-valid source
  `changerail.delivery-run.v1` record
- **AND** it does not wrap that record in an unschematized attention-view object

### Requirement: Status reader surfaces canonical runtime attention links
The single-card status reader MUST derive related runtime artifact paths only
from the validated status record and effective workspace, and MUST use existing
schemas before showing linked manifest pause guidance.

#### Scenario: Related runtime paths are shown when unambiguous
- **WHEN** the selected delivery-run status is valid
- **THEN** human-readable output includes repository-relative canonical paths
  for the related delivery manifest, review verdict, review history and
  retained evidence index when each path can be derived unambiguously
- **AND** missing related artifacts are shown as missing or omitted without
  guessing alternate runtime locations

#### Scenario: Manifest pause reasons are shown from structured fields
- **WHEN** the related delivery manifest exists, validates as
  `changerail.delivery-manifest.v1` and contains `runtime_pause_reasons`
- **THEN** human-readable output prints each existing pause reason `summary`
  and `next_action`
- **AND** the command does not infer pause guidance from raw stdout, raw stderr,
  process trees or free-text agent session logs

#### Scenario: Invalid linked runtime artifact is not trusted
- **WHEN** a related manifest, verdict or evidence index exists but fails its
  schema validation
- **THEN** human-readable output marks the linked artifact invalid
- **AND** the command exits non-zero instead of presenting its contents as
  trusted attention guidance

### Requirement: Single-card status reader smoke coverage
ChangeRail MUST include focused deterministic smoke coverage for the
single-card status reader.

#### Scenario: Smoke covers status success and diagnostics
- **WHEN** the delivery runner smoke suite runs
- **THEN** it covers successful explicit-path status reading
- **AND** it covers run-id or latest status selection
- **AND** it covers blocked or no-go terminal diagnostics
- **AND** it covers manifest pause reason rendering
- **AND** it covers corrupt or unsupported status input failure

#### Scenario: Smoke proves read-only behavior
- **WHEN** the single-card status smoke reads status, manifest, verdict or
  evidence runtime artifacts
- **THEN** the smoke verifies that the command did not change those artifacts'
  content

### Requirement: Runner captures delivery performance summary
The delivery runner MUST record best-effort performance data from child JSONL
events and workspace runtime evidence in the delivery run status record.

#### Scenario: Child emits command lifecycle events
- **WHEN** a fake child JSONL stream contains command start and completion
  events for multiple commands
- **THEN** the runner status includes command execution count
- **AND** it includes command duration summaries with runner-observed durations

#### Scenario: Child emits agent messages
- **WHEN** a child JSONL stream contains agent message events
- **THEN** the runner status includes an agent message count when that event
  class is observed

#### Scenario: Child reaches terminal outcome
- **WHEN** a child JSONL stream or fallback evidence determines a terminal
  outcome
- **THEN** the runner status includes the terminal outcome and available timing
  summary without changing the existing `DELIVERED`, `NO-GO` or `BLOCKED`
  semantics

### Requirement: Runner provides child discovery budget policy
The delivery runner MUST provide runner-launched children with a compact
public-safe discovery budget or policy that describes bounded output
expectations.

#### Scenario: Runner launches delivery child
- **WHEN** the runner starts a non-interactive delivery child
- **THEN** the child receives a discovery policy through prompt text,
  environment or another structured handoff available to the child
- **AND** the policy identifies bounded discovery patterns and the documented
  per-command output threshold

#### Scenario: Policy is generic across consumer repositories
- **WHEN** the runner prepares the child discovery policy
- **THEN** the policy avoids codebase-language assumptions, private workspace
  names and raw runtime log content
- **AND** the policy does not require shell interception to be enforceable

#### Scenario: Raw evidence is retained separately
- **WHEN** command stdout or stderr is retained for runtime evidence
- **THEN** the discovery policy does not make ignored raw evidence committable
- **AND** the child-facing policy remains a bounded summary of expected
  behavior rather than a copy of raw command output

### Requirement: Runner records bounded command output metadata
The delivery runner MUST record bounded per-command output metadata in delivery
run status when structured child events provide sufficient data.

#### Scenario: Command event reports output bytes
- **WHEN** child JSONL exposes command completion data with stdout or stderr
  byte counts
- **THEN** `status.json` records bounded command output-byte metadata for that
  command
- **AND** the record does not copy raw stdout or stderr payload text into the
  structured status

#### Scenario: Command exceeds output threshold
- **WHEN** a command's observed output bytes exceed the documented
  per-command threshold
- **THEN** `status.json` marks that command as threshold-exceeded
- **AND** the status retains only bounded metadata and references to ignored raw
  evidence when such references are available

### Requirement: Runner distinguishes command result and truncation states
The delivery runner MUST distinguish command process failure, runner-observed
truncation and successful bounded result when structured child events provide
enough fields.

#### Scenario: Command fails without truncation
- **WHEN** a command completion event reports a non-zero exit code without a
  truncation indicator
- **THEN** the command metadata records a process-failure classification

#### Scenario: Command output is runner-truncated
- **WHEN** a command event or runner observation reports output truncation
- **THEN** the command metadata records a truncation classification separate
  from process failure

#### Scenario: Command succeeds within budget
- **WHEN** a command completion event reports success and output bytes within
  the threshold
- **THEN** the command metadata records a successful bounded result

#### Scenario: Structured output fields are unavailable
- **WHEN** child JSONL lacks sufficient fields to classify command output
- **THEN** the runner reports the optional output classification as unknown or
  absent instead of scraping arbitrary stdout/stderr text

### Requirement: Runner records episode and attempt lineage
The delivery runner MUST write stable episode identity and typed attempt
identity into new single-card run status records.

#### Scenario: New delivery starts an episode
- **WHEN** the runner starts a new single-card delivery without a supported
  source status
- **THEN** status records contain an `episode.id` and a `delivery` attempt id
  matching the run id

#### Scenario: Resume links to source attempt
- **WHEN** the runner resumes from a schema-valid blocked status
- **THEN** the new status keeps the source episode id
- **AND** it records a `recovery` attempt with previous/source-status linkage

### Requirement: Runner reports complete totals with bounded samples
The delivery runner MUST keep aggregate command/timeline totals independent of
bounded retained detail samples.

#### Scenario: Command details are sampled
- **WHEN** observed commands exceed the retained command detail limit
- **THEN** status records include observed count, retained count, limit and
  truncation state
- **AND** `command_execution_count` and aggregate duration still represent all
  observed completed commands

#### Scenario: Progress events define wait intervals
- **WHEN** accepted value-free lifecycle progress events describe active stages
  and waiting stages
- **THEN** status records can expose active, wait and operator-wait duration
  totals
- **AND** rejected content-bearing progress events do not affect those totals

### Requirement: Runner reports oversized command summary
The delivery runner MUST print a sanitized operator-facing summary of top
oversized commands when command output metadata exceeds the documented
threshold.

#### Scenario: Oversized commands exist
- **WHEN** a delivery run records commands whose output exceeds the threshold
- **THEN** runner terminal output identifies the top oversized commands with
  sanitized labels, byte counts and threshold information
- **AND** it provides remediation that points operators toward scoped paths,
  file-name discovery, counts or bounded excerpts

#### Scenario: Command label contains sensitive-looking material
- **WHEN** an oversized command label contains URL userinfo, token-like
  assignments or local runtime paths
- **THEN** the operator-facing summary redacts or omits those values before
  printing or writing structured summary fields

### Requirement: Oversized output smoke remains bounded
ChangeRail delivery runner smoke MUST prove that oversized command output is
accounted for without copying raw payloads into status records.

#### Scenario: Synthetic child emits oversized command output
- **WHEN** the delivery runner smoke launches a synthetic child that emits
  oversized command output
- **THEN** the runner status records byte accounting and threshold metadata
- **AND** the status record remains below the documented bounded size
- **AND** the raw oversized payload does not appear in `status.json`

#### Scenario: Raw evidence remains ignored
- **WHEN** the synthetic oversized output smoke retains raw stdout or stderr
  evidence
- **THEN** the evidence path remains under ignored runtime state
- **AND** delivery manifest or scoped publish helpers do not treat it as a
  committable path

### Requirement: Runner timestamps observed JSONL events
The delivery runner MUST preserve runner-observed timing for child JSONL events
used in performance summaries.

#### Scenario: Timeline is retained
- **WHEN** the runner records a timeline entry or equivalent command summary
- **THEN** each retained event has a runner-observed timestamp or duration
  derived from runner observation order
- **AND** raw child stdout remains ignored runtime evidence

### Requirement: Explicit terminal outcomes
The runner MUST report terminal outcomes `DELIVERED`, `NO-GO` and `BLOCKED`
without relying on free-text log interpretation.

#### Scenario: Codex exits successfully
- **WHEN** the non-interactive delivery command exits `0`
- **AND** Codex JSONL contains no authoritative terminal outcome
- **AND** structured workspace evidence proves the current card is uniquely
  published under `openspec/board/4.done`
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

### Requirement: Authoritative terminal events для delivery runner
Delivery runner MUST выводить `NO-GO` и `BLOCKED` terminal outcomes только из
documented structured event types, explicit terminal outcome fields или exact
terminal marker lines в completed agent-message event и MUST NOT рекурсивно
интерпретировать arbitrary JSON string values как terminal outcomes или
reasons.

#### Scenario: Non-terminal tool error перед published successful exit
- **WHEN** Codex JSONL содержит non-terminal tool result со string values вроде
  `error` или `failed`, process завершается `0`, а карточка опубликована
- **THEN** runner записывает `DELIVERED`

#### Scenario: Authoritative fix-budget handoff
- **WHEN** completed agent-message event содержит exact lines
  `terminal_outcome: BLOCKED` и
  `terminal_reason: fix_budget_exhausted`
- **THEN** runner записывает и печатает оба machine-readable значения
- **AND** завершает wrapper non-zero

#### Scenario: Authoritative terminal reason is malformed
- **WHEN** authoritative terminal event содержит reason, который не является
  lowercase snake-case code
- **THEN** runner сохраняет terminal outcome
- **AND** записывает `terminal_reason: malformed_terminal_reason` вместо
  молчаливого удаления или принятия некорректного classifier

#### Scenario: Authoritative no-go event
- **WHEN** Codex JSONL содержит documented structured no-go event
- **THEN** runner записывает и печатает terminal outcome `NO-GO`

#### Scenario: Awaiting review event
- **WHEN** Codex JSONL содержит documented `awaiting-review` или
  `awaiting-external-review` event
- **THEN** runner записывает и печатает terminal outcome `BLOCKED`

#### Scenario: Conflicting terminal events учитывают order
- **WHEN** Codex JSONL содержит несколько authoritative terminal events
- **THEN** runner использует последний authoritative terminal event в stdout
  order

#### Scenario: Non-zero exit без authoritative outcome
- **WHEN** Codex завершается non-zero и stdout не содержит authoritative
  terminal outcome
- **THEN** runner записывает `BLOCKED`

### Requirement: Review-gated safety-stop fallback
The runner MUST fail closed when no authoritative terminal event exists and
structured card or review evidence does not prove that review-gated publish
completed.

#### Scenario: Fresh no-go verdict after successful child exit
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict for that card validates fresh with
  `result: no-go`
- **THEN** the runner records `NO-GO`
- **AND** the wrapper exits non-zero

#### Scenario: Invalid or stale verdict after successful child exit
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** the current card is not published under `openspec/board/4.done`
- **AND** the canonical review verdict for that card exists but fails validation
  or freshness checks
- **THEN** the runner records `BLOCKED`
- **AND** the wrapper exits non-zero

#### Scenario: Unpublished card without verdict after successful child exit
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** no canonical review fallback applies
- **AND** the current card is not uniquely published under
  `openspec/board/4.done`
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: unpublished_card`
- **AND** the wrapper exits non-zero

#### Scenario: Published card preserves successful fallback
- **WHEN** Codex exits `0` without an authoritative terminal outcome
- **AND** the current card has been moved under `openspec/board/4.done`
- **THEN** stale ignored review runtime evidence alone MUST NOT override the
  successful fallback outcome

#### Scenario: Batch supervisor stops after fallback no-go
- **WHEN** a supervisor runs single-card runner invocations sequentially
- **AND** the first runner invocation exits non-zero with `NO-GO` from fallback
  review evidence
- **THEN** the supervisor MUST NOT start the next card in that batch

### Requirement: One-command delivery regression smoke
ChangeRail MUST provide deterministic delivery-runner smoke coverage that starts
from a deliver-ready board card and proves the runner-supervised
`$changerail-deliver` path through observable repository and runtime state.

#### Scenario: One-command delivery success fixture
- **WHEN** the delivery runner smoke runs its one-command success fixture
- **THEN** the fixture uses a temporary Git repository and local bare remote
  without live network access
- **AND** the fixture starts from a `2.todo` deliver-ready card and invokes one
  runner orchestration entrypoint for that card
- **AND** the final card location, local Git history, remote branch, delivery
  manifest, review verdict, retained evidence and runner status are mutually
  consistent
- **AND** tracked card text does not contain stale mutable publish metadata such
  as exact commit hash or push status
- **AND** manifest scope excludes ignored runtime evidence and contains no extra
  committable paths outside the card-owned payload

#### Scenario: One-command delivery resumes after transient preflight
- **WHEN** the smoke simulates a transient remote publish-target preflight
  failure before launch
- **THEN** the first runner status records a blocked preflight with sanitized
  remote failure evidence
- **AND** an explicit `resume --status-path <status.json>` run repeats fresh
  preflight and publishes only after the local bare remote is reachable
- **AND** the resumed terminal status is `DELIVERED` for the same card

#### Scenario: One-command delivery fails closed on stale verdict
- **WHEN** the smoke provides a stale canonical review verdict for an unpublished
  card after a child exits successfully without authoritative delivery evidence
- **THEN** the runner records `BLOCKED`
- **AND** the card remains outside `4.done`
- **AND** no payload commit is pushed to the local bare remote

#### Scenario: One-command delivery fails closed on exhausted review budget
- **WHEN** the smoke simulates a final external review `NO-GO` after the
  same-card review rescue budget is exhausted
- **THEN** the runner records `NO-GO` or a documented review-gated blocked
  terminal outcome
- **AND** the card remains unpublished
- **AND** no payload commit is pushed to the local bare remote

### Requirement: Delivery runner preflight
The runner MUST provide a preflight mode that checks the Codex launcher,
effective `CODEX_HOME`, auth state, `CODEX_HOME` config, stale symlinks,
executable permissions and optional connectivity URL.
Delivery runner preflight MUST sanitize connectivity diagnostics before writing
structured runtime status.

The runner MUST fail closed before launching a delivery child unless the
effective `CODEX_HOME/config.toml` grants unattended mutation authority with
`approval_policy = "never"` and `sandbox_mode = "danger-full-access"`.

#### Scenario: Effective Codex authority is insufficient
- **WHEN** preflight reads an effective Codex config with missing or different
  approval/sandbox values
- **THEN** preflight reports a blocking `Codex automation authority` check
- **AND** no delivery child is launched

#### Scenario: Connectivity check is requested
- **WHEN** an operator supplies a connectivity URL for preflight
- **THEN** the runner performs an actual connection attempt and records pass or
  fail in structured output

#### Scenario: Auth or wiring is stale
- **WHEN** auth markers are absent or `CODEX_HOME` contains broken symlinks
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

### Requirement: ChangeRail delivery runner namespace
The non-interactive delivery runner MUST use ChangeRail command, schema and
runtime names after the rename.

#### Scenario: Runner starts a delivery
- **WHEN** the post-rename runner is invoked for a board card
- **THEN** it launches the ChangeRail delivery skill through
  `$changerail-deliver <card-path>`
- **AND** it writes status records using the `changerail.delivery-run.v1`
  schema id

#### Scenario: Runtime root is defaulted
- **WHEN** the runner is invoked without an explicit runtime root
- **THEN** status and logs are written under `.runtime/changerail/delivery-runs`

### Requirement: Runner remains a single-card launcher
The tracked non-interactive delivery runner MUST treat its positional `card`
argument as one card path and MUST NOT imply that it owns multi-card queue
semantics unless explicit queue support is implemented.

#### Scenario: Operator reads runner help
- **WHEN** an operator runs `bin/changerail-delivery-runner run --help`
- **THEN** the help text describes the positional argument as a single
  repository-relative board card path

#### Scenario: Supervisor reads run status
- **WHEN** the runner writes
  `.runtime/changerail/delivery-runs/<run-id>/status.json`
- **THEN** the status record represents the single card passed to that runner
  invocation

### Requirement: Queue semantics belong to deliver or future queue runner
Documentation MUST state that directory or ordered-card queue handling belongs
to `$changerail-deliver` itself, or to a future queue-aware runner with
per-card records.

#### Scenario: Batch delivery is documented
- **WHEN** docs describe bounded batch delivery
- **THEN** they distinguish `$changerail-deliver <board-column>` from
  `bin/changerail-delivery-runner run <single-card>`

### Requirement: Queue plan input contract
The delivery runner MUST accept queue plans only through the explicit
`changerail.delivery-plan.v1` contract and MUST preserve existing single-card
runner compatibility.

#### Scenario: Single-card runner remains compatible
- **WHEN** an operator invokes `bin/changerail-delivery-runner run <card>`
- **THEN** the positional card argument is still treated as one card path
- **AND** no queue semantics are inferred from that command

#### Scenario: Queue plan is schema-backed
- **WHEN** an operator invokes a plan-oriented command
- **THEN** the runner validates the plan against
  `schemas/changerail-delivery-plan.schema.json` before applying queue
  semantics

#### Scenario: Queue status is schema-backed
- **WHEN** the runner writes aggregate queue status
- **THEN** the JSON uses `changerail.delivery-plan-status.v1` and validates
  against `schemas/changerail-delivery-plan-status.schema.json`

### Requirement: Queue plan public-safety constraints
The delivery runner MUST fail closed on queue plan values that would put
credentials, secrets or machine-specific tracked state into public plans or
status.

#### Scenario: Workspace path is absolute
- **WHEN** a queue plan workspace path is an absolute machine path
- **THEN** plan validation fails before any child delivery can launch

#### Scenario: Runtime status references logs indirectly
- **WHEN** aggregate queue status includes child evidence
- **THEN** it references structured child status paths and does not inline raw
  stdout or stderr logs

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

### Requirement: Delivery plan generation helper
The delivery runner MUST provide a non-live helper command that generates a
schema-backed queue plan from ordered card paths and optional dependency
declarations.

#### Scenario: Operator generates a serial plan
- **WHEN** an operator invokes `bin/changerail-delivery-runner generate-plan`
  with a plan id, workspace alias/path and ordered card paths
- **THEN** the command emits a `changerail.delivery-plan.v1` JSON plan whose
  cards preserve the input order
- **AND** no child delivery process is started

#### Scenario: Operator adds dependencies
- **WHEN** an operator supplies dependency declarations for generated card ids
- **THEN** the emitted plan records those dependencies under the matching card
  entries
- **AND** invalid dependency references fail before writing the plan

#### Scenario: Generated plan uses existing validation
- **WHEN** `generate-plan` emits or writes a plan
- **THEN** the payload validates against
  `schemas/changerail-delivery-plan.schema.json`
- **AND** the generated plan can be consumed by `plan` and `preflight-plan`
  without live child delivery

### Requirement: Queue preflight validation
The delivery runner MUST fail closed during `preflight-plan` before launching
any live child delivery when plan, workspace, git or card state is inconsistent.

#### Scenario: Plan has invalid dependency graph
- **WHEN** a plan contains a dependency cycle, missing dependency id or
  dependency that points to an invalid later wave
- **THEN** `preflight-plan` records `BLOCKED` aggregate status and exits
  non-zero before any child launch

#### Scenario: Plan has duplicate identifiers
- **WHEN** a plan contains duplicate workspace aliases or duplicate card ids
- **THEN** `preflight-plan` records `BLOCKED` aggregate status and exits
  non-zero

#### Scenario: Concurrency settings conflict
- **WHEN** `max_parallel` is less than one or per-workspace parallelism allows
  more than one live card in a workspace
- **THEN** `preflight-plan` records `BLOCKED` aggregate status and exits
  non-zero

#### Scenario: Workspace readiness fails
- **WHEN** a workspace is missing, is not a git repository, lacks the configured
  single-card runner readiness, or has unsafe initial git/card state
- **THEN** `preflight-plan` records the failing check in aggregate status and
  exits non-zero

### Requirement: Stable queue card resolution
The delivery runner MUST resolve queue cards by stable filename or card id
across board lanes before listing, preflighting, running or resuming a plan.

#### Scenario: Card moved after plan was written
- **WHEN** a plan references a card filename that currently exists in exactly
  one board lane
- **THEN** the runner uses the current card path in the resolved plan

#### Scenario: Card is missing or duplicated
- **WHEN** a plan card cannot be found or resolves to more than one board path
- **THEN** the plan command fails closed before any child launch

#### Scenario: Card is canceled
- **WHEN** a plan card resolves under `openspec/board/5.canceled/`
- **THEN** the plan command fails closed unless an explicit future operator
  override is implemented and recorded

### Requirement: Queue preflight aggregate status
The delivery runner MUST write schema-backed aggregate status for plan preflight
and status inspection, and MUST surface child preflight failures as compact
operator diagnostics without embedding raw child logs.

#### Scenario: Preflight succeeds
- **WHEN** `preflight-plan` validates every workspace, card and dependency
- **THEN** aggregate status records `DELIVERED` as the preflight result, the
  plan fingerprint and all resolved card states without child run references

#### Scenario: Operator reads status
- **WHEN** an operator invokes `status-plan` for a prior queue run or preflight
- **THEN** the command reads the aggregate status record and reports structured
  queue state without parsing raw child stdout or stderr

#### Scenario: Child preflight failure summary is compact
- **WHEN** `preflight-plan` observes a child preflight check failure
- **THEN** aggregate operator output reports the card id, failing check name,
  `fail` status and a short reason
- **AND** the output does not rely on a truncated child JSON blob

#### Scenario: Child preflight evidence remains referenced
- **WHEN** aggregate status records a child preflight failure
- **THEN** the corresponding card entry includes a concise `reason` and a
  `run_status_path` reference to the child `changerail.delivery-run.v1` status
  record
- **AND** aggregate status does not inline raw stdout or stderr logs

#### Scenario: JSON status remains schema-compatible
- **WHEN** `status-plan --json` reads aggregate status with compact child
  diagnostics
- **THEN** the emitted JSON still validates against
  `schemas/changerail-delivery-plan-status.schema.json`

### Requirement: Live queue plan execution
The delivery runner MUST execute `run-plan` by launching the existing
single-card runner once for each live card that is ready by dependency and wave.

#### Scenario: Child card starts
- **WHEN** a card becomes runnable in `run-plan`
- **THEN** the queue runner invokes `bin/changerail-delivery-runner run <card>`
  for that card's resolved workspace
- **AND** the child writes a separate `changerail.delivery-run.v1` status record

#### Scenario: Queue preserves workspace serialization
- **WHEN** multiple runnable cards belong to the same workspace
- **THEN** at most one card from that workspace is live at a time

#### Scenario: Queue allows cross-workspace parallelism
- **WHEN** runnable cards belong to dependency-independent workspaces
- **THEN** the queue runner may run them in parallel up to `max_parallel`

### Requirement: Queue dependency and wave barriers
The delivery runner MUST enforce plan dependencies and wave barriers
deterministically during live and resumed queue execution.

#### Scenario: Dependency is incomplete
- **WHEN** a card depends on another card whose terminal outcome is not a
  successful queue outcome
- **THEN** the dependent card is not launched

#### Scenario: Wave barrier blocks downstream cards
- **WHEN** a later wave contains cards but an earlier wave has unfinished or
  failed cards
- **THEN** the later wave is not launched

### Requirement: Queue fail-fast terminal outcomes
The delivery runner MUST stop launching new downstream cards when a live child
or queue validation reaches an unsafe terminal outcome. Autonomous recovery
after child `NO-GO` or `fix_budget_exhausted` MUST be represented as a linked
rescue/replacement card before dependent downstream cards resume.

#### Scenario: Child returns no-go
- **WHEN** a child delivery run returns `NO-GO`
- **THEN** aggregate queue status records `NO-GO`
- **AND** no new downstream cards are launched

#### Scenario: Child exhausts fix budget
- **WHEN** a child delivery run returns `BLOCKED` with
  `terminal_reason: fix_budget_exhausted`
- **THEN** aggregate queue status preserves that terminal reason
- **AND** no new downstream cards are launched

#### Scenario: Autonomous recovery is represented as a card
- **WHEN** an autonomous agent continues after a terminal child `NO-GO` or
  `fix_budget_exhausted`
- **THEN** it MUST create or run a linked rescue/replacement card carrying
  `recovery_for` rather than pushing the failed child payload
- **AND** dependent downstream cards remain blocked until recovery publishes
  through a fresh independent `GO`

#### Scenario: Child returns blocked
- **WHEN** a child delivery run returns `BLOCKED` for an external or unavailable
  condition
- **THEN** aggregate queue status records `BLOCKED`
- **AND** no new downstream cards are launched or automatic recovery card is
  inferred

#### Scenario: Repository state is inconsistent after child success
- **WHEN** child status reports `DELIVERED` but card location, git cleanliness,
  upstream equality or no-push ahead-state success checks fail
- **THEN** aggregate queue status records `BLOCKED`

#### Scenario: Child status is missing or invalid
- **WHEN** a queue child exits but its delivery-run status is missing or has an
  unsupported result
- **THEN** aggregate queue status records `BLOCKED` with
  `missing_or_invalid_child_status` regardless of process exit code

### Requirement: Queue workspace locks
The delivery runner MUST use ignored workspace locks to prevent concurrent live
queue children in the same repository.

#### Scenario: Workspace lock exists
- **WHEN** a queue attempts to launch a card in a workspace with an active lock
- **THEN** the launch is blocked with structured diagnostics

#### Scenario: Lock appears stale
- **WHEN** a workspace lock appears older than the current run
- **THEN** the runner reports stale-lock diagnostics
- **AND** it does not delete the lock automatically without an explicit safe
  operator action

### Requirement: Safe queue resume
The delivery runner MUST implement `resume-plan` without re-running already
successful queue cards, without trusting unrelated plan drift, and with one
constrained recovery-plan augmentation after a recoverable terminal child.

#### Scenario: Resume sees delivered card
- **WHEN** aggregate status shows a card succeeded and current workspace state
  still satisfies the selected push or no-push success criteria
- **THEN** `resume-plan` skips that card

#### Scenario: Resume sees moved unfinished card
- **WHEN** an unfinished card has moved to another non-canceled board lane
- **THEN** `resume-plan` re-resolves the current card path before launching it

#### Scenario: Plan fingerprint changes without valid recovery augmentation
- **WHEN** the current plan fingerprint differs from aggregate status and the
  change is not limited to valid added `recovery_for` cards
- **THEN** `resume-plan` records `BLOCKED` and exits non-zero before launching
  unfinished cards

#### Scenario: Plan adds a valid recovery card
- **WHEN** a changed plan preserves all previous card identity, workspace, card
  reference, wave and dependencies
- **AND** every added card is a unique same-workspace, same-wave recovery for a
  prior `NO-GO` card or prior `fix_budget_exhausted` card
- **THEN** `resume-plan` accepts the recovery augmentation and launches the
  recovery before dependants of the failed source

#### Scenario: Recovery publishes successfully
- **WHEN** the recovery child returns `DELIVERED` and normal queue publish-state
  checks pass
- **THEN** aggregate status marks the source `recovered` and records
  `recovered_by`
- **AND** only then may the source id satisfy downstream dependencies

#### Scenario: Recovery fails
- **WHEN** the recovery child returns `NO-GO`, `BLOCKED` or inconsistent publish
  state
- **THEN** aggregate queue remains fail-fast and does not launch source
  dependants

### Requirement: Queue success criteria
The delivery runner MUST distinguish push-enabled and explicit `--no-push`
queue success criteria.

#### Scenario: Push-enabled card succeeds
- **WHEN** a child returns `DELIVERED` in push-enabled mode
- **THEN** queue success for that card requires exactly one card location under
  `openspec/board/4.done/`, a clean owning repository and `HEAD == upstream`

#### Scenario: No-push card succeeds
- **WHEN** a child returns `DELIVERED` in explicit `--no-push` mode
- **THEN** queue success for that card requires a committed clean tree and the
  expected ahead-of-upstream state recorded in aggregate status

### Requirement: Per-card queue overrides
The delivery runner MUST support per-card model and reasoning overrides from
the plan without changing repository defaults.

#### Scenario: Card override is declared
- **WHEN** a plan card declares model or reasoning effort
- **THEN** the corresponding single-card child invocation receives those
  overrides for that run only

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
- **AND** the docs describe default `<workspace>/.codex` `CODEX_HOME`
  resolution and explicit `CODEX_HOME` override behavior

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

### Requirement: Actionable auth remediation diagnostics
Delivery runner preflight MUST keep missing-auth and stale-symlink checks
fail-closed while reporting concise remediation guidance that does not expose
credential contents.

#### Scenario: Auth marker is missing
- **WHEN** delivery runner preflight finds no supported auth marker and no
  supported auth environment variable
- **THEN** the `CODEX auth` check fails
- **AND** its message points to the project-local auth marker, explicit
  `CODEX_HOME` or supported auth environment variable remediation path

#### Scenario: Auth symlink is stale
- **WHEN** delivery runner preflight finds a broken symlink under effective
  `CODEX_HOME`
- **THEN** the `CODEX_HOME symlinks` check fails
- **AND** its message identifies stale symlink diagnostics and points to the
  auth setup remediation path

#### Scenario: Diagnostics stay sanitized
- **WHEN** runner preflight records auth remediation diagnostics
- **THEN** structured status does not include credential file contents,
  environment variable values or token-like secret values

### Requirement: Delivery runner uses shared Python runtime
`bin/changerail-delivery-runner` MUST execute every subcommand through the
shared ChangeRail Python runtime selector.

#### Scenario: Runner starts with supported runtime
- **WHEN** an operator invokes `bin/changerail-delivery-runner run <card>`
- **THEN** the shared selector validates the interpreter and required modules
- **AND** runner preflight or delivery launch behavior proceeds normally

#### Scenario: Runner override is invalid
- **WHEN** `CHANGERAIL_PYTHON` points to an invalid interpreter and an operator
  invokes any delivery runner subcommand
- **THEN** the runner exits non-zero before preflight or delivery child launch
- **AND** the diagnostic identifies the invalid override

### Requirement: Remote publish-target preflight diagnostics
The delivery runner MUST classify remote-push publish-target preflight failures
and MUST retain sanitized structured evidence in `changerail.delivery-run.v1`
status without relying on raw child logs.

#### Scenario: SSH config failure is classified
- **WHEN** single-card preflight cannot prove the publish target because Git or
  SSH reports SSH configuration, identity, key setup or host key setup failure
- **THEN** the `publish target` preflight check fails with
  `failure_class: ssh_config`
- **AND** the status contains only sanitized remote name, branch, remote URL
  class, command summary and bounded detail

#### Scenario: DNS failure is classified
- **WHEN** single-card preflight cannot resolve the remote host while proving
  the publish target
- **THEN** the `publish target` preflight check fails with
  `failure_class: dns`
- **AND** the failure is marked retryable

#### Scenario: Auth failure is classified
- **WHEN** single-card preflight reaches the remote but authentication or
  authorization is denied
- **THEN** the `publish target` preflight check fails with
  `failure_class: auth`
- **AND** the failure is not marked retryable

#### Scenario: Missing branch is classified
- **WHEN** `git ls-remote --exit-code` proves the remote exists but the selected
  upstream branch ref is absent
- **THEN** the `publish target` preflight check fails with
  `failure_class: missing_branch`
- **AND** the failure is not marked retryable

#### Scenario: Timeout is classified
- **WHEN** publish-target proof times out before `git ls-remote` returns
- **THEN** the `publish target` preflight check fails with
  `failure_class: timeout`
- **AND** the failure is marked retryable

#### Scenario: Unknown remote failure is classified
- **WHEN** publish-target proof fails for a remote condition that does not
  match a more specific class
- **THEN** the `publish target` preflight check fails with
  `failure_class: unknown_remote_failure`
- **AND** the failure remains fail-closed

### Requirement: Bounded transient remote preflight retry
The delivery runner MUST apply bounded retry/backoff only to transient remote
preflight classes and MUST stop immediately on authority or branch uncertainty.

#### Scenario: Transient class is retried
- **WHEN** remote-push preflight fails with `failure_class: dns`, `timeout` or
  `unknown_remote_failure`
- **THEN** the runner may repeat the publish-target proof up to the configured
  bounded attempt count
- **AND** the final status records attempt count and final sanitized evidence

#### Scenario: Non-transient class is not retried
- **WHEN** remote-push preflight fails with `failure_class: ssh_config`,
  `auth` or `missing_branch`
- **THEN** the runner does not retry automatically
- **AND** the final status remains `BLOCKED`

### Requirement: Explicit single-card resume after remote preflight failure
The delivery runner MUST provide an explicit single-card resume path that
accepts prior status for context, repeats full fresh preflight, and launches
delivery only after the selected publish target is proven.

#### Scenario: Resume succeeds after later publish-target proof
- **WHEN** prior single-card status is `BLOCKED` by a remote-push preflight
  failure
- **AND** the operator invokes single-card `resume` with that status
- **AND** fresh preflight now proves the upstream branch through `git ls-remote`
- **THEN** the runner launches `$changerail-deliver` for the current card path
- **AND** the new status records fresh preflight evidence rather than trusting
  the prior failed status

#### Scenario: Resume fails closed on stale or unsafe prior status
- **WHEN** prior status is missing, invalid, belongs to another workspace/card,
  or did not stop at a recoverable remote preflight failure
- **THEN** single-card `resume` records `BLOCKED` and exits non-zero before
  launching delivery

#### Scenario: Resume repeats the full preflight
- **WHEN** single-card `resume` is invoked
- **THEN** the runner re-runs launcher, auth, config, symlink, permission and
  publish-target checks for the current workspace
- **AND** no prior preflight check is treated as a pass

### Requirement: Queue remote preflight diagnostics
The delivery runner MUST propagate child remote publish-target preflight
diagnostics through queue preflight and status records as compact structured
operator evidence.

#### Scenario: Queue preflight reports child remote class
- **WHEN** `preflight-plan` observes a child `publish target` preflight failure
  with a remote `failure_class`
- **THEN** aggregate card status includes a compact reason with that class and
  a `run_status_path` reference to the child `changerail.delivery-run.v1`
  status
- **AND** aggregate status does not inline raw child stdout or stderr

#### Scenario: Queue resume requires fresh child proof
- **WHEN** `resume-plan` continues after a prior child remote preflight stop
- **THEN** the queue runner launches a fresh child run or preflight for the
  unresolved card
- **AND** downstream cards remain blocked until that child satisfies normal
  push-enabled or explicit `--no-push` success criteria

### Requirement: Investigation-required retained payload identity
The delivery runner MUST record schema-valid retained-payload identity when a
single-card delivery child stops with `terminal_outcome: BLOCKED`,
`terminal_reason: investigation_required`, and leaves an unreviewed working-tree
payload for possible recovery.

#### Scenario: Runner records retained identity at safety stop
- **WHEN** a delivery child reports `BLOCKED` with
  `terminal_reason: investigation_required`
- **AND** the workspace still contains the unreviewed payload that triggered
  deterministic review preflight
- **THEN** the runner status includes a `retained_payload` object
- **AND** that object identifies the source run, card, workspace, `HEAD` commit,
  reviewed tree SHA, diff fingerprint and working-tree review target

#### Scenario: Identity capture failure remains blocked
- **WHEN** the runner cannot compute a canonical retained-payload fingerprint
  after an `investigation_required` stop
- **THEN** the runner keeps the terminal outcome `BLOCKED`
- **AND** it records a stable machine diagnostic for missing retained-payload
  identity instead of silently accepting an unverifiable resume target

### Requirement: Retained identity excludes raw payload evidence
The delivery runner MUST keep retained-payload identity bounded to metadata and
MUST NOT copy raw source payload, raw child stdout/stderr, secrets or ignored
runtime evidence into tracked files as proof for a later resume.

#### Scenario: Raw logs are not retained as identity
- **WHEN** the runner records retained-payload identity for an
  `investigation_required` stop
- **THEN** the identity contains fingerprint and path metadata only
- **AND** raw child logs remain referenced through ignored runtime paths rather
  than embedded in card, schema or OpenSpec artifacts

#### Scenario: WIP references are not identity proof
- **WHEN** a blocked status names a WIP commit, stash, branch name or prose
  assertion but lacks the schema-valid retained-payload fingerprint
- **THEN** ChangeRail does not treat that reference as retained-payload identity

### Requirement: Explicit single-card resume after investigation required
The delivery runner MUST provide an explicit single-card resume path that
accepts a prior `changerail.delivery-run.v1` status only when it belongs to the
same card and workspace, has `terminal_outcome: BLOCKED`,
`terminal_reason: investigation_required`, and contains matching
retained-payload identity.

#### Scenario: Resume succeeds after published authorization
- **WHEN** prior single-card status stopped at `investigation_required`
- **AND** its retained-payload identity matches the current workspace and card
- **AND** the published investigation and bounded authorization sources are
  tracked, clean at `HEAD` and relation-matched to the current card
- **THEN** single-card `resume --status-path <status.json>` continues to the
  review/publish portion for the retained working-tree payload
- **AND** the resumed status records fresh deterministic preflight evidence

#### Scenario: Resume rejects mismatched status identity
- **WHEN** prior status is missing, schema-invalid, stale, belongs to another
  card or belongs to another workspace
- **THEN** single-card resume records `BLOCKED`
- **AND** it exits non-zero before launching a child continuation
- **AND** it records a stable machine reason for the mismatch

#### Scenario: Resume rejects payload drift
- **WHEN** the prior status contains retained-payload identity
- **AND** the current `HEAD`, reviewed tree SHA or diff fingerprint differs from
  that identity outside the clean tracked authorization sources
- **THEN** single-card resume records `BLOCKED`
- **AND** it does not treat the current working tree as the retained review
  target

### Requirement: Retained resume does not trust checkpoint commits
Single-card retained-payload resume MUST preserve the dirty working tree as the
review target and MUST NOT treat a WIP commit, stash name, branch name or prose
assertion as a substitute for retained-payload fingerprint proof.

#### Scenario: Checkpoint commit is not review evidence
- **WHEN** an operator provides a commit or branch that contains the unreviewed
  payload but the prior retained-payload fingerprint does not match the current
  working tree
- **THEN** resume remains `BLOCKED`
- **AND** the runner does not use that commit or branch as independent review
  evidence

#### Scenario: Ordinary launch remains clean-tree gated
- **WHEN** the operator starts `run`, `run-plan` or a remote-preflight resume
  without a valid prior `investigation_required` or
  `recoverable_external_blocker` retained-payload status
- **THEN** the existing clean-workspace launch requirements remain in force

### Requirement: Recoverable external blocker stop
Delivery runner MUST считать temporary external blocker recoverable только
когда authoritative structured child event объявляет known blocker class,
bounded resume-evidence requirements и canonical retained-payload identity.

#### Scenario: Required external gate временно недоступен
- **WHEN** delivery child сообщает `BLOCKED` со schema-valid recoverable
  external blocker на mandatory platform, service, credential, license или
  required-software gate
- **THEN** runner записывает bounded blocker и exact retained identity
- **AND** не сообщает delivery success и не обходит последующий review

#### Scenario: Free-text blocker не является authoritative
- **WHEN** child prose или stderr описывает external blocker без structured
  contract либо называет unknown/nonrecoverable class
- **THEN** runner оставляет attempt blocked и non-resumable
- **AND** не разрешает dirty workspace на основании этого текста

### Requirement: Evidence-bound retained external resume
Single-card resume MUST запускать child с dirty workspace только когда prior
status identity, blocker class, exact retained fingerprint и все declared fresh
recovery evidence проходят валидацию. Evidence доказывает только retry
eligibility; resumed lifecycle MUST повторить mandatory verification и
review/publish gates.

#### Scenario: External condition восстановлен
- **WHEN** оператор передает schema-valid evidence index в scope source run/card
  со всеми required passed entries новее blocker
- **AND** current workspace и retained fingerprint точно совпадают с prior
  status
- **THEN** resume запускает original card с value-free recovery context
- **AND** resumed child повторяет mandatory external gate до возможного delivery
  success

#### Scenario: Resume input stale или mismatched
- **WHEN** evidence отсутствует, stale, failed, относится к другому run/card
  либо payload/workspace identity drifted
- **OR** target-bound recovery evidence has missing, mismatched or multiple
  entry target identities
- **THEN** resume завершается non-zero до Codex launch
- **AND** status записывает stable machine-classified blocker reason

### Requirement: Queue resume after investigation-required child
The delivery runner MUST allow `resume-plan` to represent recovery from a prior
child with `terminal_reason: investigation_required` only when the prior child
status is schema-valid, belongs to the same workspace/card source and contains
matching retained-payload identity.

#### Scenario: Queue resumes original retained payload
- **WHEN** aggregate status contains a child `BLOCKED` with
  `terminal_reason: investigation_required`
- **AND** the child status contains matching retained-payload identity
- **AND** the current plan fingerprint is unchanged
- **THEN** `resume-plan` may launch single-card
  `resume --status-path <prior-child-status>` for that original card
- **AND** downstream cards remain blocked until that child publishes
  successfully

#### Scenario: Queue accepts one replacement recovery card
- **WHEN** the current plan adds one recovery card for a prior
  `investigation_required` source
- **AND** all previous card identity, workspace, card reference, wave and
  dependencies are preserved
- **AND** the recovery card is same-workspace, same-wave and inherits the source
  dependencies
- **THEN** `resume-plan` accepts the recovery augmentation
- **AND** it launches the recovery before dependants of the source

#### Scenario: Queue blocks unsafe investigation recovery
- **WHEN** prior child status is missing, schema-invalid, from another
  workspace/card, lacks retained-payload identity or no longer matches the
  current retained payload
- **THEN** `resume-plan` records `BLOCKED`
- **AND** it exits non-zero before launching the source or downstream cards

### Requirement: Queue parity for recoverable external blocker
`resume-plan` MUST валидировать и возобновлять original externally blocked child
до продолжения dependency queue, сохраняя completed cards и workspace
serialization.

#### Scenario: Original child успешно возобновляется
- **WHEN** aggregate plan содержит одну valid retained external recovery и
  supplied evidence проходит
- **THEN** `resume-plan` сначала запускает эту карточку, а затем освобождает ее
  downstream dependencies после normal delivery success
- **AND** уже delivered prior plan карточки остаются skipped

#### Scenario: Duplicate или mixed recovery отклоняется
- **WHEN** plan state объявляет несколько recovery paths для одной source card
  либо recovery identity принадлежит другому workspace/card
- **THEN** queue resume fail closed до запуска child
- **AND** downstream cards остаются explicitly blocked

### Requirement: Queue recovery keeps downstream blocked
Queue recovery from `investigation_required` MUST NOT satisfy downstream
dependencies until the original retained payload or its explicit replacement
has passed the risk-appropriate independent review and publish checks.

#### Scenario: Original retained payload publishes successfully
- **WHEN** retained-payload resume returns `DELIVERED` and normal queue
  publish-state checks pass
- **THEN** aggregate status may mark the source delivered
- **AND** only then may downstream dependencies treat that source as satisfied

#### Scenario: Replacement recovery publishes successfully
- **WHEN** a valid recovery card returns `DELIVERED` and normal queue
  publish-state checks pass
- **THEN** aggregate status marks the source `recovered` and records
  `recovered_by`
- **AND** only then may downstream dependencies treat that source as satisfied

#### Scenario: Recovery fails closed
- **WHEN** retained-payload resume or replacement recovery returns `NO-GO`,
  `BLOCKED` or inconsistent publish state
- **THEN** aggregate queue status remains fail-fast
- **AND** no source dependants are launched

### Requirement: Queue retained recovery smoke coverage
ChangeRail MUST include focused synthetic smoke coverage for
`investigation_required` queue recovery.

#### Scenario: Smokes cover success and adversarial cases
- **WHEN** the queue recovery smoke suite runs
- **THEN** it covers successful retained recovery
- **AND** it covers dirty state, stale authorization, wrong card, wrong
  workspace and fingerprint drift failures
- **AND** it covers successful external blocker recovery, stale/missing
  evidence, payload drift, mixed workspaces, nonrecoverable blockers and target
  identity mismatches

### Requirement: Runner SHALL retain exact execution target identity
Delivery runner SHALL capture canonical declared target identity at attempt
start и SHALL сохранять ее через single-card status, plan status, blocker и
resume lineage без physical endpoint или credentials.

#### Scenario: Identity остается стабильной
- **WHEN** preflight, child terminal status и current declaration содержат exact
  same id/fingerprint
- **THEN** lifecycle может продолжиться к review/publish gates

#### Scenario: Declaration drifted во время delivery
- **WHEN** current tracked target identity отличается от captured identity
- **THEN** runner завершает path как blocked
- **AND** не запускает downstream card и не публикует payload

### Requirement: Runner SHALL reject target substitution on resume
Single-card и package resume SHALL запускать retained payload только при exact
target identity match и SHALL NOT принимать evidence или CLI input как rebind
authority.

#### Scenario: Retained identity mismatch
- **WHEN** source status, current declaration или recovery evidence имеют
  разные target identities
- **THEN** resume fail closed до Codex launch со stable target-mismatch reason

#### Scenario: Explicit rebind выполнен
- **WHEN** оператор публикует новую tracked declaration
- **THEN** старый retained attempt остается non-resumable
- **AND** новый clean delivery получает новую captured identity

### Requirement: External recovery SHALL NOT substitute a declared target
Runner MUST сохранять exact declared execution target across retained resume и
MUST завершаться до Codex launch при target drift или попытке использовать
recovery как authority на создание, переподключение или подмену среды.

#### Scenario: Recovery evidence указывает другую цель
- **WHEN** evidence target id/fingerprint или target-bound entry
  id/fingerprint не совпадает с source retained identity
- **THEN** single-card и queue resume fail closed со stable target-mismatch
  reason
- **AND** child не запускается и downstream queue не освобождается.

#### Scenario: Оператор явно переподключил среду
- **WHEN** tracked project target identity изменилась после blocked attempt
- **THEN** dirty retained resume недоступен
- **AND** оператор начинает новый clean delivery attempt с новой verification
  lineage.

### Requirement: Delivery episode and attempt lineage
ChangeRail runner MUST назначать stable episode id одному card execution и
unique typed attempt id каждому preflight, delivery или recovery process.
Resume MUST наследовать source episode и ссылаться на source attempt;
unrelated new execution той же карточки MUST начинать другой episode.

#### Scenario: Blocked child возобновляется
- **WHEN** schema-valid blocked attempt возобновляется через supported
  single-card или plan workflow
- **THEN** resumed status сохраняет source `episode_id`, использует новый
  recovery attempt id и связывает previous/source attempt
- **AND** card/workspace/episode identity проверяется до launch

#### Scenario: Та же карточка начинает unrelated execution
- **WHEN** оператор запускает new run без authorized source status
- **THEN** runner создает новый episode id
- **AND** prior attempts и review cycles не присоединяются только по card id

### Requirement: Complete aggregate performance with bounded samples
Runner MUST сохранять aggregate counts и durations всех observed commands,
tools и structured phases, даже когда detailed samples bounded. Он MUST
указывать observed count, retained count, sample limit и truncation state.

#### Scenario: Long run превышает detail limits
- **WHEN** command или timeline details превышают configured retained limits
- **THEN** aggregate counts и durations по-прежнему включают каждый observed
  item
- **AND** sample metadata сообщает truncation и effective limits

#### Scenario: Наблюдается structured operator wait
- **WHEN** lifecycle записывает value-free external/operator wait transition
- **THEN** performance totals классифицируют duration отдельно от active time
- **AND** entered value, screen content и external response не сохраняются
