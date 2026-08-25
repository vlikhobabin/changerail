## ADDED Requirements

### Requirement: Published bounded structural public-history authorization source
ChangeRail MUST publish
`authorize-bounded-structural-public-history-scan` as one clean tracked
`4.done` board card before creating successor
`deliver-structurally-bounded-public-history-scan`. The authorization source
MUST contain exactly one schema-valid `Investigation authorization` object
with only `investigation_card`, `investigation_id`, `successor_card`,
`successor_id`, `production_loc_ceiling` and
`allow_new_authority_or_wire_protocol`. Those fields MUST bind exact published
investigation `investigate-structural-public-history-scan-proof` to exact future
successor `deliver-structurally-bounded-public-history-scan` through canonical
`4.done` and `3.inprogress` paths, ceiling `301` and protocol allowance
`false`. The authorization MUST NOT raise the successor's independent limit of
300 added production LOC relative to
`ccccb62562e1646b595119edd3326763860f14a7`.

#### Scenario: Authorization source publishes before successor creation
- **WHEN** maintainers deliver the bounded structural public-history
  authorization after publication of its investigation
- **THEN** the payload contains only the authorization board card, its
  OpenSpec artifacts and the exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, no successor
  card or code is created, and no history scan, benchmark or full baseline is
  run

#### Scenario: Exact reciprocal lineage is retained for the future successor
- **WHEN** the authorization source is published and a later separate flow
  creates `deliver-structurally-bounded-public-history-scan`
- **THEN** the published investigation blocks both
  `authorize-bounded-structural-public-history-scan` and
  `deliver-structurally-bounded-public-history-scan`, while the authorization
  source depends on the investigation and blocks that exact successor
- **AND** the future successor depends on
  `investigate-structural-public-history-scan-proof` and its
  `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}`

#### Scenario: Structural authorization mismatch fails closed
- **WHEN** a future card changes any investigation, authorization or successor
  id/path, omits a reciprocal relation, uses an authorization reference with
  fields other than exact `authorization_card` and `authorization_id`, exceeds
  300 added production LOC against `ccccb625`, or declares new authority or
  wire protocol
- **THEN** deterministic verification rejects the source for that candidate
- **AND** ceiling `301` cannot authorize a 301st production line, another
  successor or a reusable authority/protocol waiver
