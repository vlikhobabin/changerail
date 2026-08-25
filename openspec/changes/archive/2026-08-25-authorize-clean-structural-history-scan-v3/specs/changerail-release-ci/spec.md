## ADDED Requirements

### Requirement: Published clean structural-history v3 authorization source
ChangeRail MUST publish `authorize-clean-structural-history-scan-v3` as one
clean tracked `4.done` board card before creating
`deliver-clean-structural-history-scan-v3`. The authorization source MUST
contain exactly one schema-valid `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`, exactly
`{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/deliver-clean-structural-history-scan-v3.md","successor_id":"deliver-clean-structural-history-scan-v3","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}`.
The authorization MUST NOT raise the future H implementation limit of `<=349`
production LOC against its published authorization HEAD, and it MUST NOT grant
new authority or wire protocol.

#### Scenario: Authorization publishes before H successor creation
- **WHEN** maintainers deliver the clean structural-history v3 authorization
  after publication of its clean-lineage decision
- **THEN** the payload contains only the authorization board card, its
  OpenSpec artifacts and this exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, no successor
  card or code is created, and no history scan, full baseline or live run is
  performed

#### Scenario: Reciprocal H lineage and ownership are retained
- **WHEN** this authorization source is published and a later separate flow
  creates `deliver-clean-structural-history-scan-v3`
- **THEN** the published decision blocks both
  `authorize-clean-structural-history-scan-v3` and
  `deliver-clean-structural-history-scan-v3`, while the authorization depends
  on the decision and blocks that exact successor
- **AND** the future successor depends on
  `rescue-private-release-loop-acceleration-publication-boundary` and its
  `Published investigation authorization` contains only exact inline JSON
  `{"authorization_card":"openspec/board/4.done/authorize-clean-structural-history-scan-v3.md","authorization_id":"authorize-clean-structural-history-scan-v3"}`
- **AND** H owns only bounded structural history traversal, Git-compatible
  parsing, memoization, non-mutation and focused/CI history ownership proof

#### Scenario: Clean structural-history authorization mismatch fails closed
- **WHEN** a candidate changes any bound id/path/relation, uses an authorization
  reference with fields other than exact `authorization_card` and
  `authorization_id`, exceeds 349 production LOC against its published
  authorization HEAD, declares new authority or wire protocol, or claims
  ownership outside H
- **THEN** deterministic verification rejects the source for that candidate
- **AND** ceiling `350` cannot authorize a 350th production line, another
  successor or a reusable authority/protocol waiver
