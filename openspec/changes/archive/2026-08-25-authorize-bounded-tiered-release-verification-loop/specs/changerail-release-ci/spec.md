## ADDED Requirements

### Requirement: Published bounded tiered release verification authorization source
ChangeRail MUST publish
`authorize-bounded-tiered-release-verification-loop` as one clean tracked
`4.done` board card before creating successor
`implement-tiered-release-verification-loop`. The authorization source MUST
contain exactly one schema-valid `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. Those
fields MUST bind exact published investigation
`investigate-tiered-release-verification-loop-boundary` to exact future
successor `implement-tiered-release-verification-loop` through canonical
`4.done` and `3.inprogress` paths, ceiling `500` and protocol allowance `true`.
The authorization MUST NOT raise the successor's independent limit of 499
executable LOC relative to
`45a2de98924c61bb9e944767013ea09918bba4b0` or authorize credential, mutation or
live authority.

#### Scenario: Authorization source publishes before successor creation
- **WHEN** maintainers deliver the bounded tiered release verification
  authorization after publication of its investigation
- **THEN** the payload contains only the authorization board card, its OpenSpec
  artifacts and the exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, no successor card
  or code is created, and no history scan, benchmark or full baseline is run

#### Scenario: Exact reciprocal lineage is retained for the future successor
- **WHEN** the authorization source is published and a later separate flow
  creates `implement-tiered-release-verification-loop`
- **THEN** the published investigation blocks both
  `authorize-bounded-tiered-release-verification-loop` and
  `implement-tiered-release-verification-loop`, while the authorization source
  depends on the investigation and blocks that exact successor
- **AND** the future successor depends on
  `investigate-tiered-release-verification-loop-boundary` and its `Published
  investigation authorization` field contains only exact inline JSON
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-tiered-release-verification-loop.md","authorization_id":"authorize-bounded-tiered-release-verification-loop"}`

#### Scenario: Tiered authorization mismatch fails closed
- **WHEN** a future card changes any investigation, authorization or successor
  id/path, omits a reciprocal relation, uses an authorization reference with
  fields other than exact `authorization_card` and `authorization_id`, exceeds
  499 executable LOC against `45a2de9`, or claims authority outside the
  decision-defined affected/full-release boundary
- **THEN** deterministic verification rejects the source for that candidate
- **AND** ceiling `500` cannot authorize a 500th executable line, another
  successor, credential/mutation/live authority or a reusable
  authority/protocol waiver
