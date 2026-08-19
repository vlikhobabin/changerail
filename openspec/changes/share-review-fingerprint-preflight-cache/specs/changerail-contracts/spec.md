## ADDED Requirements

### Requirement: Canonical review fingerprint consumers
ChangeRail MUST use one canonical review fingerprint implementation for review
preflight, review verdict freshness validation and publish gate freshness
checks.

#### Scenario: Review gates observe the same payload identity
- **WHEN** review preflight, `bin/changerail-review-verdict validate --check-fresh`
  and the publish gate run against the same workspace state
- **THEN** they observe identical `head_commit`, `tree_sha` and
  `diff_fingerprint` values
- **AND** a mismatch in any of those values continues to fail publish before
  staging

#### Scenario: Canonical implementation changes
- **WHEN** the review fingerprint implementation is updated
- **THEN** review preflight, verdict validation and publish freshness checks use
  the updated implementation without maintaining divergent freshness logic

### Requirement: Validated review fingerprint cache
ChangeRail MUST validate ignored runtime review fingerprint cache entries before
reuse. It MAY reuse them only when cheap current workspace checks prove the
cache binds the exact current payload, and MUST fail closed or recompute before
emitting freshness values when that proof is unavailable.

#### Scenario: Repeated unchanged preflight reuses cache
- **WHEN** review preflight runs twice for an unchanged workspace
- **THEN** the second run may reuse a cache entry whose HEAD and changed path
  metadata match the current workspace
- **AND** the reused result includes the same reviewed `tree_sha` and
  `diff_fingerprint` as a full canonical recomputation

#### Scenario: Workspace change invalidates cache
- **WHEN** tracked content, tracked path state, untracked non-ignored content or
  Git exclude behavior changes after a cache entry is written
- **THEN** the next freshness check recomputes the canonical fingerprint before
  emitting `tree_sha` or `diff_fingerprint`

#### Scenario: Cache remains ignored runtime state
- **WHEN** cache entries are written
- **THEN** they live under ignored `.runtime/changerail/` state
- **AND** tracked cards, manifests, specs and docs do not store cache payloads

#### Scenario: Malformed cache fails closed
- **WHEN** a cache entry is unreadable, malformed or missing required freshness
  fields
- **THEN** the helper ignores it or exits non-zero
- **AND** it does not emit approximate freshness data from the malformed entry
