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
