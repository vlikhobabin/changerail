## ADDED Requirements

### Requirement: Published bounded isolated release case executor authorization source
ChangeRail MUST publish
`authorize-bounded-isolated-release-case-executor-v2` as one clean tracked
`4.done` board card before creating successor
`implement-bounded-isolated-release-case-executor-v2`. The authorization source
MUST contain exactly one schema-valid `Investigation authorization` object with
only `investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. The object
MUST equal `{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-isolated-release-case-executor-v2.md","successor_id":"implement-bounded-isolated-release-case-executor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
The authorization payload MUST add no authority or wire protocol and MUST keep
production, test, runtime and executable LOC at `0`. The allowance MUST apply
only to the future I scope and MUST NOT authorize credential, mutation, live or
terminal authority.

#### Scenario: Authorization source publishes before I successor creation
- **WHEN** maintainers deliver the bounded I authorization after publication of
  `rescue-private-release-loop-acceleration-publication-boundary`
- **THEN** the payload contains only the authorization board card, its OpenSpec
  artifacts and this release-CI relationship requirement
- **AND** no successor card/code, production, tests or runtime state is created
  and no history scan, full release baseline or live run is performed

#### Scenario: Exact I lineage and ownership remain bounded
- **WHEN** the authorization source is published and a later separate flow
  creates `implement-bounded-isolated-release-case-executor-v2`
- **THEN** the published decision blocks both authorization and successor, the
  authorization depends on the decision and blocks that exact successor, and
  the successor depends on the decision
- **AND** the successor's `Published investigation authorization` field contains
  only exact inline JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-isolated-release-case-executor-v2.md","authorization_id":"authorize-bounded-isolated-release-case-executor-v2"}`
- **AND** the successor is limited to `<=499` executable LOC relative to its
  exact published authorization HEAD and owns only isolated case schemas,
  jobs/order, hard output/timeout bounds, process containment, cleanup and
  parsed-CI ownership proof

#### Scenario: I authorization mismatch fails closed
- **WHEN** a candidate changes any decision, authorization or successor id/path,
  omits reciprocal relations, uses fields other than exact `authorization_card`
  and `authorization_id`, exceeds `499` executable LOC, or claims registry
  selection, history parsing, receipts or terminal authority
- **THEN** deterministic verification rejects the candidate
- **AND** ceiling `500` cannot authorize a 500th executable line, another
  successor, a new authorization payload protocol, credential/mutation/live
  authority or ownership outside I scope
