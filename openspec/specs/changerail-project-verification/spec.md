# changerail-project-verification Specification

## Purpose
Зафиксировать red/green gate, который проверяет, что consumer project
подключен к ChangeRail source of truth и имеет project-local config, OpenSpec
validation и runtime/auth ignore policy.
## Requirements
### Requirement: Consumer project verification gate
ChangeRail MUST provide `bin/verify-project <path>` as a fail-closed gate for
consumer project wiring and baseline configuration.
The verifier MUST report a stable machine-readable summary status of `pass`,
`pass-with-diagnostics` or `fail`.
The verifier MUST exit `0` only for `pass` and `pass-with-diagnostics`; it MUST
exit non-zero for `fail`.

#### Scenario: Valid consumer project passes verification
- **WHEN** `bin/verify-project /opt/example-project` runs against a correctly
  wired consumer project with no blocking failures or non-blocking diagnostics
- **THEN** it exits `0` after checking symlink-и, configs, OpenSpec validation,
  helper/schema reachability and ignored runtime/auth paths
- **AND** the machine-readable summary status is `pass`

#### Scenario: Invalid consumer project fails verification
- **WHEN** required ChangeRail wiring, config, ignore policy or mandatory
  OpenSpec validation is missing or failing
- **THEN** `bin/verify-project` exits non-zero and reports the failed check
- **AND** the machine-readable summary status is `fail`

#### Scenario: Consumer project passes with explicit diagnostics
- **WHEN** all blocking checks pass and one or more explicitly non-blocking
  diagnostics are present
- **THEN** `bin/verify-project` exits `0`
- **AND** the machine-readable summary status is `pass-with-diagnostics`
- **AND** the diagnostic entries remain visible in text and JSON output

### Requirement: Полное покрытие ChangeRail contract schemas
`verify-project` и его smoke checks MUST валидировать reachability для каждой
public ChangeRail contract schema, tracked в source repository.

#### Scenario: Все public schemas существуют
- **WHEN** `bin/verify-project <path>` запускается для consumer project
- **THEN** он проверяет review verdict, review preflight result, review cycle
  history, delivery manifest, delivery run и evidence index schema files

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
Verification MUST recognize exact MCP npm package pins passed to `npx` as the
direct package argument, `--package=<package>@<version>` or
`--package <package>@<version>`.

#### Scenario: Config scope is project-local
- **WHEN** verification inspects MCP and Codex config
- **THEN** filesystem scope and trust settings cover the consumer project root
  instead of the ChangeRail repository root

#### Scenario: Verifier accepts locked direct and package-option pins
- **WHEN** `bin/verify-project <path>` inspects consumer MCP config containing
  `npx` commands for `@playwright/mcp@0.0.68` or
  `chrome-devtools-mcp@0.20.3`
- **AND** each package is passed as a direct package argument,
  `--package=<package>@<version>` or `--package <package>@<version>`
- **AND** each package/version is present in `mcp-npm-lock.json` with matching
  trusted npm registry integrity
- **THEN** package pin verification passes for those optional browser MCP
  entries

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

#### Scenario: Successful npm warnings do not corrupt integrity verification
- **WHEN** `npm view <package>@<version> dist.integrity --json` exits zero,
  returns the locked integrity JSON in stdout and emits a warning in stderr
- **THEN** `bin/verify-project` compares only the stdout payload with the lock
- **AND** the stderr warning does not produce a false integrity mismatch

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
Missing-auth output MUST identify a real ChangeRail source runbook and provide a
generic executable remediation command for existing-project configuration.

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
- **AND** it reports a warning advisory with a ChangeRail source runbook path
- **AND** it prints a generic `--configure-existing --link-codex-auth` command
  without embedding a local auth source path or credential value

### Requirement: Verify-project uses shared Python runtime
`bin/verify-project` MUST execute through the shared ChangeRail Python runtime
selector before project verification imports or checks run.

#### Scenario: Verify-project starts on supported runtime
- **WHEN** an operator runs `bin/verify-project /opt/example-project` with a
  supported Python runtime and required runtime modules
- **THEN** the shared selector starts the verifier
- **AND** project wiring verification proceeds normally

#### Scenario: Verify-project sees unsupported runtime
- **WHEN** an operator runs `bin/verify-project /opt/example-project` with an
  unsupported selected interpreter
- **THEN** verification exits non-zero before project checks run
- **AND** the diagnostic describes the supported Python runtime and remediation

### Requirement: Verification profile surface policy
`verify-project` MUST support a tracked project profile that classifies Codex,
Claude and legacy MCP surfaces as `required`, `optional` or `forbidden`.
When no profile is declared, the default profile MUST preserve the current
strict all-surfaces behavior.
Required surface failures MUST be blocking.
Forbidden surface presence MUST be blocking.
Optional missing surfaces MUST NOT be blocking, but MUST remain visible as
non-blocking diagnostics when reported.

#### Scenario: Codex-only consumer omits optional Claude surface
- **WHEN** a consumer profile marks Codex surfaces as `required` and Claude
  surfaces as `optional`
- **AND** the project has valid Codex wiring but no Claude command or skill
  surface
- **THEN** `bin/verify-project <path> --json` reports the missing Claude
  surface as a non-blocking diagnostic
- **AND** the summary status is `pass-with-diagnostics`

#### Scenario: All-surfaces default remains strict
- **WHEN** a consumer project has no profile policy
- **AND** a canonical Claude, Codex or helper surface expected by the existing
  verifier is missing
- **THEN** `bin/verify-project` reports a blocking failed check
- **AND** the summary status is `fail`

#### Scenario: Forbidden surface is present
- **WHEN** a consumer profile marks a legacy MCP surface or stale legacy
  artifact as `forbidden`
- **AND** the project contains that surface
- **THEN** `bin/verify-project` reports a blocking failed check identifying the
  forbidden artifact
- **AND** the summary status is `fail`

### Requirement: Stable check status and severity contract
Every `verify-project` check and diagnostic emitted in JSON MUST include a
stable `name`, `status`, `severity` and `message`.
The verifier MUST use `pass`, `fail` or `skip` for check status and `blocking`,
`non-blocking` or `info` for severity.
A `skip` status MUST NOT hide a required or forbidden surface failure.

#### Scenario: JSON output separates status and severity
- **WHEN** `bin/verify-project /opt/example-project --json` emits check data
- **THEN** each check object contains `name`, `status`, `severity` and
  `message`
- **AND** a failed blocking check contributes to summary `failed`
- **AND** a failed non-blocking diagnostic contributes to summary diagnostics
  without making the summary status `fail`

#### Scenario: Required check cannot be weakened by skip
- **WHEN** a profile marks targeted card-owned OpenSpec validation or required
  source wiring as `required`
- **AND** the project attempts to mark that check as `optional` or skip it
- **THEN** `bin/verify-project` reports a blocking policy error
- **AND** the summary status is `fail`

### Requirement: Targeted OpenSpec validation remains mandatory
`verify-project` MUST keep targeted card-owned OpenSpec validation mandatory
whenever a project declares the relevant card-owned change or validation target.
Profile policy MUST NOT allow a project to downgrade that targeted validation
to a non-blocking diagnostic.

#### Scenario: Targeted card-owned validation fails
- **WHEN** a consumer profile declares project-wide baseline debt as
  non-blocking
- **AND** targeted card-owned OpenSpec validation fails
- **THEN** `bin/verify-project` reports the targeted validation as blocking
- **AND** the summary status is `fail`

### Requirement: Project-wide baseline debt policy
`verify-project` MUST support treating project-wide baseline OpenSpec debt as a
non-blocking diagnostic only when tracked project policy explicitly names the
baseline command, residual risk and reason it is not card-owned.
Without that tracked policy, project-wide baseline validation failure MUST
remain blocking.

#### Scenario: Tracked residual risk allows baseline diagnostic
- **WHEN** tracked project policy declares a project-wide OpenSpec baseline debt
  entry with command, residual risk and non-card-owned rationale
- **AND** the project-wide baseline validation fails for that declared debt
- **THEN** `bin/verify-project` reports a non-blocking diagnostic
- **AND** the summary status is `pass-with-diagnostics` when no blocking checks
  fail

#### Scenario: Undeclared baseline debt fails closed
- **WHEN** project-wide OpenSpec validation fails
- **AND** no tracked policy explicitly allows that debt as a diagnostic
- **THEN** `bin/verify-project` reports a blocking failed check
- **AND** the summary status is `fail`

### Requirement: Profile and severity smoke coverage
ChangeRail MUST provide deterministic smoke coverage for verification profiles,
severity summaries and mandatory check hardening.

#### Scenario: Smoke covers profile matrix
- **WHEN** `python3 scripts/smoke-verify-project.py` runs
- **THEN** it covers Codex-only, default all-surfaces and forbidden artifact
  fixtures
- **AND** it fails if profile-aware status/severity behavior regresses

#### Scenario: Smoke covers mandatory check weakening
- **WHEN** `python3 scripts/smoke-verify-project.py` runs
- **THEN** it includes a fixture that attempts to weaken a mandatory targeted
  check
- **AND** the smoke fails unless `verify-project` reports that attempt as a
  blocking failure

### Requirement: Generated Windows wiring verification
`verify-project` MUST verify generated Windows wiring ownership, freshness and
project-owned divergence when a consumer declares generated wiring policy.

#### Scenario: Generated wiring is fresh
- **WHEN** `bin/verify-project <path>` inspects a consumer with generated
  Windows wiring policy
- **THEN** each generated-owned command, skill and helper artifact matches the
  recorded source identity and digest
- **AND** verification passes that wiring check

#### Scenario: Generated wiring is stale
- **WHEN** a generated-owned artifact no longer matches the recorded digest or
  ChangeRail source identity
- **THEN** `verify-project` exits non-zero
- **AND** the output identifies the stale artifact and refresh remediation path

#### Scenario: Project-owned divergence is present
- **WHEN** a required wiring path is project-owned or missing generated
  ownership metadata under generated Windows policy
- **THEN** `verify-project` exits non-zero
- **AND** the output distinguishes project-owned divergence from stale
  generated-copy drift

### Requirement: Windows fallback proof verification
`verify-project` MUST fail closed when Windows symlink or junction fallback
policy lacks positive proof.

#### Scenario: Symlink fallback policy is declared
- **WHEN** verification inspects a native Windows consumer that declares
  symlink fallback wiring
- **THEN** it requires recorded positive Developer Mode or symlink privilege
  proof
- **AND** the proof MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** missing or negative proof is a blocking failure

#### Scenario: Junction fallback policy is declared
- **WHEN** verification inspects a native Windows consumer that declares
  junction fallback wiring
- **THEN** it requires recorded link-aware cleanup and Git-safety proof
- **AND** the proof MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** missing or negative proof is a blocking failure

### Requirement: Generated Windows wiring verification smoke matrix
ChangeRail MUST provide deterministic smoke coverage proving that
`verify-project` accepts only fresh generated Windows wiring and fails closed on
stale, missing or project-owned generated artifacts.

#### Scenario: Fresh generated wiring passes
- **WHEN** `python3 scripts/smoke-verify-project.py` creates a generated
  Windows consumer fixture
- **THEN** `bin/verify-project <path> --json` reports passing checks for the
  generated wiring manifest and representative generated file and directory
  artifacts

#### Scenario: Missing generated artifact fails
- **WHEN** a manifest-owned generated artifact is absent from the consumer
  fixture
- **THEN** `bin/verify-project <path> --json` exits non-zero
- **AND** the failed check identifies the missing generated artifact

#### Scenario: Stale generated artifact fails with remediation
- **WHEN** a generated-owned artifact no longer matches the current ChangeRail
  source digest
- **THEN** `bin/verify-project <path> --json` exits non-zero
- **AND** the failed check identifies stale generated wiring and the
  `--refresh-wiring` remediation path

#### Scenario: Project-owned divergence remains blocking
- **WHEN** generated wiring content diverges without matching manifest-owned
  generated state
- **THEN** `bin/verify-project <path> --json` exits non-zero
- **AND** the failed check distinguishes project-owned divergence from stale
  generated-copy drift

### Requirement: Windows wiring Git safety verification
`verify-project` and its focused smoke coverage MUST prove Windows wiring paths
are safe to stage using Git porcelain status, dry-run add and index inspection.

#### Scenario: Generated wiring is Git-safe
- **WHEN** a generated Windows consumer fixture is inspected
- **THEN** verification evidence includes `git status --porcelain`,
  `git add --dry-run` and index inspection for generated command, skill and
  helper paths
- **AND** no evidence would stage ChangeRail source, ignored runtime state,
  credentials or out-of-scope files

#### Scenario: Symlink fallback Git safety is checked
- **WHEN** a Windows symlink fallback fixture is inspected
- **THEN** Git safety evidence proves the link path itself is stageable only
  within the consumer project scope
- **AND** unsafe traversal into ChangeRail source or ignored runtime state is a
  blocking failure

#### Scenario: Junction fallback Git safety is checked
- **WHEN** a Windows junction fallback fixture is inspected
- **THEN** Git safety evidence includes porcelain status, dry-run add and index
  inspection for the junction path class
- **AND** each Git proof check explicitly reports `safe: true` and
  `unsafe_paths: []`
- **AND** any evidence that would stage out-of-scope content is a blocking
  failure

#### Scenario: Credentials are not exposed
- **WHEN** Git safety fixtures include credential-like ignored files
- **THEN** diagnostics do not print credential contents
- **AND** diagnostics do not print raw unsafe path values from the retained proof
- **AND** the checks fail closed if the credential-like path becomes stageable

### Requirement: Verify-project detects maintenance opt-in
`verify-project` MUST treat tracked maintenance policy, maintenance helper
wiring or generated maintenance ownership declarations as explicit maintenance
opt-in signals.

#### Scenario: Consumer has no maintenance artifacts
- **WHEN** `bin/verify-project <path>` inspects a consumer with no tracked
  maintenance policy, helper wiring or generated ownership declaration
- **THEN** maintenance verification is skipped as not configured
- **AND** the absence of maintenance wiring is not a failure

#### Scenario: Consumer has maintenance policy
- **WHEN** `bin/verify-project <path>` finds a tracked
  `.changerail/maintenance.yaml`
- **THEN** it treats the consumer as opted in to maintenance verification
- **AND** missing required maintenance helper, schema, config or ignore wiring
  is reported as a blocking failure

### Requirement: Verify-project validates opted-in maintenance wiring
Opted-in consumers MUST have complete maintenance helper, schema, config and
ignore wiring, but verification MUST NOT run a full maintenance scan as part of
bootstrap verification.

#### Scenario: Opted-in consumer is complete
- **WHEN** `bin/verify-project <path>` inspects an opted-in consumer with valid
  maintenance policy, reachable maintenance helper wrappers, required schemas
  and ignored runtime paths
- **THEN** verification passes the maintenance wiring check
- **AND** it does not execute `bin/changerail-maintenance scan` as part of that
  check

#### Scenario: Maintenance runtime is not ignored
- **WHEN** an opted-in consumer would allow `.runtime/changerail/maintenance/`
  content to be tracked
- **THEN** `verify-project` reports a blocking failure
- **AND** it does not print raw runtime report contents

### Requirement: Verify-project validates maintenance generated copies
`verify-project` MUST include maintenance helper copies in generated Windows
wiring freshness checks when a consumer declares generated maintenance wiring.

#### Scenario: Generated maintenance helper is fresh
- **WHEN** `verify-project` inspects an opted-in generated Windows consumer
- **THEN** maintenance helper copies match recorded source identity and digest
- **AND** the generated wiring check passes

#### Scenario: Generated maintenance helper is stale or project-owned
- **WHEN** a generated maintenance helper is missing, stale or replaced by
  project-owned content
- **THEN** `verify-project` exits non-zero
- **AND** diagnostics distinguish stale generated-copy drift from
  project-owned divergence

### Requirement: Verify-project requires complete maintenance schema inventory
`verify-project` MUST require every tracked public maintenance schema for
consumers that have opted in to maintenance wiring.

#### Scenario: Opted-in consumer has complete maintenance schemas
- **WHEN** `bin/verify-project <path>` inspects an opted-in consumer
- **THEN** it checks reachability of `changerail-maintenance-quality-rollup.schema.json`
- **AND** it checks reachability of `changerail-maintenance-proposal-decision.schema.json`
- **AND** those checks are reported alongside the other required maintenance schemas

#### Scenario: Maintenance quality schema is missing
- **WHEN** an opted-in consumer cannot reach `changerail-maintenance-quality-rollup.schema.json`
- **THEN** `verify-project` exits non-zero with a blocking schema failure
- **AND** it does not run a full maintenance scan while diagnosing the missing schema

#### Scenario: Maintenance proposal-decision schema is missing
- **WHEN** an opted-in consumer cannot reach `changerail-maintenance-proposal-decision.schema.json`
- **THEN** `verify-project` exits non-zero with a blocking schema failure
- **AND** it does not report the maintenance opt-in as complete

### Requirement: Generated-copy maintenance contracts fail closed
Generated-copy verification MUST include the full maintenance contract surface
when generated ownership metadata declares maintenance helper or schema wiring.

#### Scenario: Generated-copy maintenance wiring is fresh
- **WHEN** `verify-project` inspects an opted-in generated-copy consumer with fresh maintenance helpers and schemas
- **THEN** the generated-copy verification passes for maintenance helper and schema artifacts
- **AND** the quality-rollup and proposal-decision schema checks pass

#### Scenario: Generated-copy maintenance schema is stale
- **WHEN** a generated-copy maintenance contract artifact is stale or replaced by project-owned content
- **THEN** `verify-project` exits non-zero
- **AND** diagnostics distinguish stale generated-copy drift from project-owned divergence without printing secret-like file contents

### Requirement: Declared bootstrap profile verification
`verify-project` MUST validate the canonical project, surface and Codex authority
profiles recorded by bootstrap and MUST fail closed when generated configuration
contradicts the declared profile. Legacy consumers without canonical fields MUST
continue through the existing all-surfaces compatibility path.

#### Scenario: Codex-only consumer is coherent
- **WHEN** a consumer declares `codex-only` and contains valid Codex wiring but
  omits optional Claude wiring
- **THEN** verification reports the optional surface as a non-blocking
  diagnostic
- **AND** the profile consistency check passes

#### Scenario: Safe profile contains full-access settings
- **WHEN** a consumer declares `safe-interactive` but tracked Codex config uses
  `never` or `danger-full-access`
- **THEN** verification reports a blocking profile mismatch

#### Scenario: Legacy consumer has no canonical profiles
- **WHEN** an existing consumer has no new bootstrap profile metadata
- **THEN** verification applies the existing strict all-surfaces behavior
- **AND** does not infer trusted automation from absent metadata

### Requirement: Profile matrix regression evidence
ChangeRail MUST maintain deterministic smoke coverage for all supported project,
surface and Codex authority selections and their invalid combinations.

#### Scenario: Profile smoke runs
- **WHEN** bootstrap and verify smoke execute
- **THEN** default, codex-only, workspace-root, service and trusted-automation
  fixtures are evaluated
- **AND** invalid or conflicting values fail before target mutation

### Requirement: Consumer lock and source drift verification
`verify-project` MUST validate `changerail.consumer-lock.v1` separately from
actual wiring and source revision checks. Broken wiring MUST always be blocking;
source drift MUST be non-blocking for advisory enforcement and blocking for
strict enforcement.

#### Scenario: Locked source and wiring match
- **WHEN** the consumer lock, actual symlinks and ChangeRail version/revision
  match
- **THEN** lock, wiring and source checks pass independently

#### Scenario: Advisory source revision drifts
- **WHEN** actual ChangeRail revision differs from an advisory lock while wiring
  remains valid
- **THEN** verification returns a visible non-blocking source-drift diagnostic

#### Scenario: Strict source revision drifts
- **WHEN** actual ChangeRail revision differs from a strict lock
- **THEN** verification reports a blocking source-drift failure with lock refresh
  remediation

#### Scenario: Wiring is broken under advisory enforcement
- **WHEN** an owned symlink is missing or resolves to an unexpected source
- **THEN** verification fails regardless of advisory source enforcement

### Requirement: Lockless consumer compatibility
Existing consumers without `openspec/changerail-consumer-lock.json` MUST remain
verifiable through the existing wiring contract and MUST receive an explicit
lockless compatibility diagnostic rather than an inferred strict lock.

#### Scenario: Existing consumer has no lock
- **WHEN** verify-project inspects a valid legacy POSIX consumer
- **THEN** existing wiring checks continue to apply
- **AND** absence of the new lock alone is not a blocking failure

### Requirement: Existing-project configuration diagnostics
Verification MUST classify whether an auth or wiring remediation is safe for
bounded existing-project configuration and MUST not recommend automatic repair
for project-owned conflicts or unrelated dirty state.

#### Scenario: Missing allowlisted auth marker is repairable
- **WHEN** the ignored auth destination is absent and parent scope is valid
- **THEN** the diagnostic may recommend the configure command

#### Scenario: Destination is project-owned
- **WHEN** the auth or wiring destination contains non-owned content
- **THEN** the diagnostic reports manual owner review
- **AND** it does not recommend automatic overwrite

### Requirement: Consumer instruction budget verification
`verify-project` MUST measure effective `AGENTS.md` as UTF-8 bytes against the
tracked `project_doc_max_bytes` value. It MUST pass below 85 percent, emit a
non-blocking warning from 85 percent through the configured limit, and fail
blocking above the limit.

#### Scenario: Instructions are below warning threshold
- **WHEN** effective instructions use less than 85 percent of the tracked budget
- **THEN** the instruction budget check passes with measured and allowed bytes

#### Scenario: Instructions approach the limit
- **WHEN** effective instructions use at least 85 percent but do not exceed the
  tracked budget
- **THEN** verification returns a non-blocking warning with remediation

#### Scenario: Instructions exceed the limit
- **WHEN** effective instructions exceed `project_doc_max_bytes`
- **THEN** verification reports a blocking failure
- **AND** it recommends reducing project/shared content or explicitly reviewing
  a tracked budget change

### Requirement: Static and runtime verification separation
Default `verify-project` MUST describe Codex TOML, trust, MCP and instruction
checks as static. Effective runtime diagnostics MUST run only after explicit
operator opt-in and MUST never convert unavailable or invalid probe output into
a successful runtime claim.

#### Scenario: Default verifier runs
- **WHEN** an operator invokes `verify-project` without runtime diagnostics
- **THEN** no Codex runtime or network probe is launched
- **AND** the result makes only static configuration claims

#### Scenario: Runtime diagnostics are requested
- **WHEN** an operator passes `--runtime-diagnostics` in a supported Codex
  environment
- **THEN** version-aware structured probes inspect loaded config/trust/MCP and
  discovered instructions from the consumer context
- **AND** runtime outcome is reported separately from static summary

#### Scenario: Runtime probe is unavailable
- **WHEN** the supported Codex command or expected structured output is absent
- **THEN** runtime diagnostics report unsupported or invalid evidence
- **AND** they do not report runtime readiness

### Requirement: Runtime diagnostic evidence safety
Raw runtime output MUST be stored only under ignored
`.runtime/changerail/diagnostics/`. Machine-readable summaries MUST use an
allowlist and redact absolute local paths, credential values and raw auth data.

#### Scenario: Runtime probe contains local state
- **WHEN** structured Codex output contains home paths, auth marker locations or
  endpoint details
- **THEN** raw data remains ignored
- **AND** public-safe summary reports only classified status and redacted path
  kinds

#### Scenario: Public scan inspects diagnostic fixtures
- **WHEN** current/history public-surface checks run
- **THEN** no raw runtime report, private path or credential-like value is
  tracked

### Requirement: Adopted consumer lock verification
`verify-project` MUST distinguish legacy lockless compatibility from adopted
lock-backed wiring. After successful adoption, verification MUST validate the
consumer lock, adopted wiring inventory and source revision according to the
selected enforcement.

#### Scenario: Legacy lockless consumer remains diagnostic
- **WHEN** `verify-project` inspects a valid legacy consumer without
  `openspec/changerail-consumer-lock.json`
- **THEN** existing lockless compatibility checks remain visible
- **AND** the output does not claim that lock-backed refresh is available

#### Scenario: Adopted consumer is lock-backed
- **WHEN** `verify-project` inspects a consumer migrated by lockless adoption
- **THEN** it validates `openspec/changerail-consumer-lock.json`
- **AND** it validates that adopted wiring matches the lock-owned artifact
  inventory
- **AND** it reports source drift according to advisory or strict enforcement

#### Scenario: Adopted helper is missing
- **WHEN** a helper listed in the adopted consumer lock is missing or no longer
  matches declared ownership
- **THEN** verification reports a blocking wiring failure
- **AND** the remediation points to lock-owned `--refresh-wiring`, not another
  lockless adoption

### Requirement: Lockless adoption diagnostics
`verify-project` MUST report whether a lockless consumer appears eligible for
explicit adoption without recommending automatic overwrite for ambiguous or
project-owned surfaces.

#### Scenario: Lockless consumer appears adoptable
- **WHEN** a lockless consumer has complete required wiring resolving to one
  ChangeRail source root and no project-owned conflicts
- **THEN** verification may report an adoption advisory with a generic
  existing-project adoption command
- **AND** the advisory omits private paths and credential values

#### Scenario: Lockless consumer has ambiguous ownership
- **WHEN** verification finds dangling wiring, mixed roots, regular files or
  undeclared destinations in the wiring surface
- **THEN** it reports that automatic adoption is unsafe
- **AND** it does not recommend a command that would overwrite project-owned
  content

### Requirement: Project verification MUST validate declared target safely
`verify-project` MUST schema-validate regular tracked execution-target
declaration и MUST fail closed на unsafe path, invalid shape или content-bearing
fields без выполнения project/provider commands.

#### Scenario: Declaration schema valid
- **WHEN** optional declaration имеет exact v1 shape
- **THEN** verification сообщает target identity contract pass без вывода
  sensitive values

#### Scenario: Declaration invalid or unsafe
- **WHEN** declaration является symlink, содержит unknown fields либо не
  проходит schema
- **THEN** verification сообщает bounded failure и не запускает delivery

### Requirement: Deterministic verification coverage preflight
Review preflight MUST fail closed до model launch, когда configured coverage map,
per-change plan или runtime ledger invalid, stale, scope-incomplete либо не
содержит required observed evidence.

#### Scenario: Ledger fresh и complete
- **WHEN** map/plan/card/manifest/review fingerprints совпадают и каждая
  applicable entry имеет schema-valid fresh evidence required kinds
- **THEN** coverage process check проходит
- **AND** deterministic check не расходует semantic review budget

#### Scenario: Evidence направлен на internal disconnected path
- **WHEN** process contract complete, но linked test/oracle не exercise
  published boundary или connected integration route
- **THEN** deterministic identity check не придумывает semantic pass
- **AND** independent reviewer MUST оценить и может block test adequacy

#### Scenario: Coverage map не настроена
- **WHEN** project не имеет reference `verification.coverage_map`
- **THEN** preflight использует current project-declared verification floor
- **AND** не требует generated coverage artifacts
