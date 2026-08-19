## ADDED Requirements

### Requirement: Retained payload identity status contract
`changerail.delivery-run.v1` MUST allow an optional `retained_payload` object
using `schema: changerail.retained-payload-identity.v1`. When present for
`terminal_reason: investigation_required`, the object MUST include the source
run id, source status path, captured timestamp, card id/path, workspace root,
`HEAD` commit, reviewed tree SHA, diff fingerprint and review target kind.

#### Scenario: Schema validates retained identity
- **WHEN** a delivery-run status records an `investigation_required` retained
  payload with all required identity fields
- **THEN** `schemas/changerail-delivery-run.schema.json` validation succeeds
- **AND** the diff fingerprint matches the canonical `sha256:<hex>` format

#### Scenario: Retained identity is tied to the prior status
- **WHEN** a retained-payload identity is present
- **THEN** it names the source run id and source status path that produced the
  `investigation_required` stop
- **AND** a later consumer can compare those values with the resume input before
  evaluating the current working tree

### Requirement: Retained payload identity is public-safe
The retained-payload identity contract MUST describe only bounded metadata. It
MUST NOT require raw source content, raw command output, credentials, customer
data, absolute private project aliases beyond the existing workspace root field
or ignored runtime evidence content.

#### Scenario: Schema rejects raw retained content fields
- **WHEN** a retained-payload identity attempts to embed raw source text or raw
  stdout/stderr as required proof
- **THEN** the delivery-run schema does not accept those fields as part of the
  identity contract
- **AND** consumers rely on canonical fingerprints and explicit runtime path
  references instead
