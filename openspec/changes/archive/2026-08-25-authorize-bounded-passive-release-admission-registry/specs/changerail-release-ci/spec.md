## ADDED Requirements

### Requirement: Published bounded passive release admission authorization source
ChangeRail MUST publish
`authorize-bounded-passive-release-admission-registry` as one clean tracked
`4.done` board card before creating successor
`implement-passive-release-admission-registry`. The source MUST contain exactly
one schema-valid `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. Those
fields MUST bind exact published investigation
`rescue-tiered-release-authority-two-stage-boundary` to exact future successor
`implement-passive-release-admission-registry` through canonical `4.done` and
`3.inprogress` paths, ceiling `500` and protocol allowance `false`. Future A1
MUST remain at no more than 499 added production LOC relative to the exact
remote-reachable HEAD that publishes this authorization source.

#### Scenario: Authorization source publishes before A1 creation
- **WHEN** maintainers deliver the bounded passive admission authorization
  after publication of its rescue investigation
- **THEN** the payload contains only the authorization board card, its OpenSpec
  artifacts and the exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, successor card or
  code remains absent, and no history scan or full baseline is run

#### Scenario: Exact reciprocal lineage is retained for future A1
- **WHEN** the authorization source is published and a later separate flow
  creates `implement-passive-release-admission-registry`
- **THEN** the published rescue investigation blocks both authorization and
  future A1, while authorization depends on the rescue and blocks that A1
- **AND** future A1 depends on
  `rescue-tiered-release-authority-two-stage-boundary` and its
  `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-passive-release-admission-registry.md","authorization_id":"authorize-bounded-passive-release-admission-registry"}`

#### Scenario: A1 authorization limits passive ownership
- **WHEN** future `implement-passive-release-admission-registry` is scoped or
  reviewed against this source
- **THEN** it owns only the literal 35-record registry, canonical digest,
  owners, direct commands and sequential groups; total bounded injected
  admission; effective-PATH Python and parsed distribution-pin/Ruff-origin
  checks; offline OpenSpec admission; bounded Git A/M/D/R/C/untracked
  selection; closed path map; parsed Python-AST ownership oracle and connected
  faults
- **AND** it cannot own authority receipts, terminal capture, credentials,
  mutation, live access, A2 activation or another release entrypoint

#### Scenario: A1 remains structurally dormant through A2 publication
- **WHEN** this authorization or future A1 is delivered, reviewed or published
  before separately published `implement-terminal-release-authority-activation`
- **THEN** no release baseline, CI workflow, manifest/review/publish preflight,
  receipt schema or production entrypoint imports, invokes or activates A1
- **AND WHEN** that exact A2 is published
- **THEN** only exact published A2 may import, invoke or activate published A1
- **AND** a structural negative-wiring oracle fails every pre-A2 activation
  path and every post-A2 activation path outside exact A2

#### Scenario: Authorization and dormant A1 use current focused proof
- **WHEN** publication eligibility is assessed for this source or future A1
- **THEN** this docs-only source uses strict exact-object, relation, absence,
  ownership, current public-safety and source-classification checks, while A1
  uses real offline admission plus focused, static, current and connected fault
  proof
- **AND** neither payload executes, requires or accepts a reachable-history
  scan, full release baseline, authority receipt or terminal capture as its
  publication evidence
- **AND** prohibited evidence cannot be cited as reusable full-release authority
  for A2

#### Scenario: Passive admission authorization mismatch fails closed
- **WHEN** a card changes any rescue, authorization or successor id/path, adds
  a seventh source field, changes ceiling `500` or protocol `false`, creates A1
  before authorization publication, exceeds 499 added production LOC against
  the published authorization HEAD, expands A1 ownership or wires it before A2
- **THEN** deterministic verification rejects the source or candidate
- **AND** no malformed, partial or over-broad payload can authorize A1
