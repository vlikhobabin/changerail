## ADDED Requirements

### Requirement: Bounded review-fingerprint investigation decision
ChangeRail MUST publish a tracked investigation decision before a retained
oversized review-fingerprint implementation can authorize a bounded successor
above the ordinary production-LOC limit. The decision MUST reproduce the
public-safe production LOC breakdown, identify removable duplication or
over-expansion, bind one exact successor card and preserve exact fingerprint
freshness requirements.

#### Scenario: Investigation records bounded successor decision
- **WHEN** the investigation card is completed for the retained
  review-fingerprint payload
- **THEN** it records that the retained attempt is read-only investigation
  evidence and not review evidence
- **AND** it records the 527 production-LOC breakdown from public-safe retained
  evidence
- **AND** it binds the exact successor
  `deliver-bounded-review-fingerprint-optimization`
- **AND** it states a replacement ceiling no greater than 500 added production
  LOC without raising the global limit

#### Scenario: Successor keeps exact fingerprint verification floor
- **WHEN** the bounded successor is authorized from the investigation decision
- **THEN** the successor acceptance keeps exact reviewed-tree parity for add,
  modify, delete, rename, symlink, Unicode, spaces, literal arrow and valid
  non-UTF-8 Linux paths
- **AND** untracked-content hashing, ignored runtime exclusion, cache
  invalidation, shared freshness consumer behavior and synthetic benchmark
  coverage remain mandatory verification targets
