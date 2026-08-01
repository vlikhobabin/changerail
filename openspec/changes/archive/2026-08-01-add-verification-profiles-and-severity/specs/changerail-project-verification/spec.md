## MODIFIED Requirements

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

## ADDED Requirements

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
