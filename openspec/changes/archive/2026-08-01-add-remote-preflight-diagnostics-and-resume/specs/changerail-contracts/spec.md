## ADDED Requirements

### Requirement: Delivery run remote preflight evidence
The `changerail.delivery-run.v1` contract MUST support structured sanitized
evidence for remote-push publish-target preflight checks while keeping the
canonical top-level delivery-run fields stable.

#### Scenario: Remote preflight failure evidence validates
- **WHEN** a delivery run status records a failed `publish target` preflight
  check for a remote-push target
- **THEN** the check may include structured fields for result, remote, branch,
  remote URL class, failure class, retryability, attempt count, command summary
  and bounded sanitized detail
- **AND** the document validates against
  `schemas/changerail-delivery-run.schema.json`

#### Scenario: Delivery run does not add duplicate aliases
- **WHEN** remote preflight diagnostics are recorded
- **THEN** the delivery run status continues to use canonical top-level fields
  `schema`, `run_id`, `updated_at`, `workspace`, `card`, `phase`, `result`,
  `timestamps`, `command` and `usage`
- **AND** schema validation rejects duplicate top-level aliases such as `id`,
  `status` or `started_at`

#### Scenario: Sanitized evidence excludes raw secrets and logs
- **WHEN** remote preflight evidence is stored in delivery-run status
- **THEN** it contains no raw remote URL userinfo, token-like query values, raw
  stdout or raw stderr
- **AND** raw logs remain ignored runtime evidence referenced only by existing
  log paths when available

### Requirement: Queue status remote preflight evidence
The `changerail.delivery-plan-status.v1` contract MUST allow queue card
diagnostics to reference child remote preflight evidence without embedding raw
child logs.

#### Scenario: Queue card references child remote failure
- **WHEN** aggregate queue status records a card blocked by child remote
  publish-target preflight
- **THEN** the card entry may include a compact reason, terminal reason or
  failure class summary plus `run_status_path`
- **AND** the status validates against
  `schemas/changerail-delivery-plan-status.schema.json`
