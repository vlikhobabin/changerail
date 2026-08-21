## ADDED Requirements

### Requirement: Profile-aware source classification verification
Project verification и review preflight MUST fail closed при invalid
classification, immutable profile checksum conflict, measure conflict или
confirmed undeclared profile drift, сообщая unaccepted detection-only candidates
как non-authoritative diagnostics.

#### Scenario: Существует confirmed profile drift
- **WHEN** `check` возвращает blocking schema-valid drift finding
- **THEN** project verification/preflight сообщает blocking policy check
- **AND** semantic review не запускается с understated classification

#### Scenario: Существует low-confidence unaccepted candidate
- **WHEN** detection-only scan сообщает uncovered low-confidence candidate
- **THEN** verifier выдает non-blocking diagnostic и recommended explicit review
  action
- **AND** current risk values выводятся только из tracked classification
