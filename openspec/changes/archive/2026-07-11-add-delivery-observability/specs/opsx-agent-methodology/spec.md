## ADDED Requirements

### Requirement: Scoped rescue review loop
OPSX methodology MUST describe how a no-go review leads to scoped fixes,
re-review and publish only after a fresh go verdict.

#### Scenario: Over-claim receives no-go
- **WHEN** review finds an over-claimed publish scope or unbacked evidence
- **THEN** the implementing session fixes only the scoped blocker and requests a
  fresh review before publish

#### Scenario: Re-review returns go
- **WHEN** a later independent review returns a fresh `go` verdict
- **THEN** publish can proceed while retaining earlier no-go evidence for
  operational learning
