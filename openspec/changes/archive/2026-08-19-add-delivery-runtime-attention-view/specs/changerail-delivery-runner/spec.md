## ADDED Requirements

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
  `updated_at`, `terminal_reason` when present and the selected status path
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
