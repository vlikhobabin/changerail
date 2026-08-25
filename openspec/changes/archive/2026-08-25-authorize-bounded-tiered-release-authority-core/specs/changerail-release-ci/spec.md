## ADDED Requirements

### Requirement: Published bounded release authority core authorization source
ChangeRail MUST publish
`authorize-bounded-tiered-release-authority-core` as one clean tracked `4.done`
board card before creating successor `implement-tiered-release-authority-core`.
The source MUST contain exactly one schema-valid `Investigation authorization`
object with only `investigation_card`, `investigation_id`, `successor_card`,
`successor_id`, `production_loc_ceiling` and
`allow_new_authority_or_wire_protocol`. Those fields MUST bind exact published
rescue `rescue-tiered-release-verification-split-boundary` to that exact future
successor through canonical `4.done` and `3.inprogress` paths, ceiling `500`
and protocol allowance `true`. The authorization MUST NOT raise the independent
successor limit of `<=499` production LOC against
`25f756ebf2aa90c58e01eab3703b291dbdde257f` or authorize credential, mutation
or live authority.

#### Scenario: Scope A authorization publishes before successor creation
- **WHEN** maintainers deliver the authority-core authorization after the split
  rescue is published and remote-reachable
- **THEN** the source object is exactly
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-authority-core.md","successor_id":"implement-tiered-release-authority-core","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** the payload contains only the authorization board card, its OpenSpec
  artifacts and this release-CI relationship requirement; production, test and
  runtime additions remain zero and successor card/code stay absent

#### Scenario: Exact reciprocal lineage is retained for Scope A
- **WHEN** this source is published and a later separate flow creates
  `implement-tiered-release-authority-core`
- **THEN** the split rescue blocks both the authorization and exact successor,
  while the authorization depends on the rescue and blocks that successor
- **AND** the successor depends on both sources and its `Published investigation
  authorization` contains only
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-tiered-release-authority-core.md","authorization_id":"authorize-bounded-tiered-release-authority-core"}`

#### Scenario: Scope A ownership is exclusive
- **WHEN** the authorization or its future successor is scoped
- **THEN** it owns only aggregate toolchain admission, the exact 35-ID registry
  and digest, affected/full selection and authority, atomic marker/lock/fsync,
  generic capture identity and fingerprint equality, receipt/manifest/schema/
  preflight/publish gates, canonical CI full-runner invocation and their parsed
  YAML/Python-AST ownership oracles
- **AND** Scope B Windows schemas, jobs, isolation/order, process-group
  lifecycle, deduplication and owner transition plus verify-project, history
  scanner and review/delivery smoke internals remain excluded

#### Scenario: Authority mismatch fails closed
- **WHEN** a candidate changes any bound id/path/relation, uses more than the
  exact two reference fields, claims excluded ownership or credential/mutation/
  live authority, or adds a 500th production line against the exact base
- **THEN** deterministic verification rejects that candidate
- **AND** ceiling `500` and allowance `true` cannot authorize another successor,
  a broad waiver or reuse of forensic implementation payload
