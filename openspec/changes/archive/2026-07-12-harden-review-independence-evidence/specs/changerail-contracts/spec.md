## ADDED Requirements

### Requirement: Review independence attestation
Review verdicts MUST include a machine-checkable reviewer independence
attestation that states whether the reviewer used a fresh context and did not
plan or implement the reviewed payload.

#### Scenario: Reviewer writes a go verdict
- **WHEN** a reviewer writes `.runtime/changerail/reviews/<card-id>.json`
- **THEN** the `reviewer` object includes an independence attestation with
  `fresh_context: true`, `did_not_plan_or_implement: true` and a non-empty
  basis

#### Scenario: Publish validates a verdict without attestation
- **WHEN** `bin/changerail-review-verdict validate --check-fresh` checks a
  verdict whose reviewer independence attestation is missing or false
- **THEN** validation fails before publish can stage files

### Requirement: Independence limits are explicit
Review verdict docs MUST state that helper validation checks reviewer
attestation and working-tree freshness, but cannot by itself prove the real
identity or full memory boundary of an external agent session.

#### Scenario: Maintainer reads review contract docs
- **WHEN** a maintainer reads the review verdict reference
- **THEN** the document distinguishes machine-checked attestation from
  operator-enforced session independence
