## ADDED Requirements

### Requirement: Published bounded release child supervisor authorization source
ChangeRail MUST publish
`authorize-bounded-release-child-supervisor-v1` as one clean tracked `4.done`
board card before creating successor
`implement-bounded-release-child-supervisor-v1`. The source MUST contain
exactly one schema-valid `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. Those
fields MUST bind exact published investigation
`rescue-release-process-supervisor-boundary` to the exact future successor
through canonical `4.done` and `3.inprogress` paths, ceiling `500` and protocol
allowance `true`. Future S MUST remain at no more than 499 added production LOC
relative to the exact remote-reachable HEAD that publishes this authorization
source.

#### Scenario: Authorization source publishes before future S creation
- **WHEN** maintainers deliver the bounded child-supervisor authorization after
  the rescue investigation is published
- **THEN** the payload contains only the authorization card, its OpenSpec
  artifacts and this exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, future S
  card/code remain absent, and no history scan, full-release baseline or live
  execution is run

#### Scenario: Exact reciprocal lineage is retained for future S
- **WHEN** the authorization source is published and a later separate flow
  creates `implement-bounded-release-child-supervisor-v1`
- **THEN** the published rescue blocks both authorization and future S, while
  this authorization depends on the rescue and blocks only future S
- **AND** future S depends on `rescue-release-process-supervisor-boundary` and
  its `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-release-child-supervisor-v1.md","authorization_id":"authorize-bounded-release-child-supervisor-v1"}`

#### Scenario: S authorization limits protocol and POSIX ownership
- **WHEN** future `implement-bounded-release-child-supervisor-v1` is scoped or
  reviewed against this source
- **THEN** it owns only the platform-neutral child protocol and POSIX hard
  stdout/stderr/report framing, process-group containment, finite deadline,
  TERM-then-KILL escalation, reaping and subreaper cleanup
- **AND** Git parsing, scheduler policy, Windows Job behavior, registry,
  baseline/CI activation, receipt ownership, credential authority, mutation
  authority and live admission are excluded and scope overlap fails closed

#### Scenario: S remains structurally dormant through A3 publication
- **WHEN** this authorization or future S is delivered, reviewed or published
  before exact `implement-payload-bound-release-authority-v3` is published and
  remote-reachable
- **THEN** `run-release-baseline`, the CI workflow, review/publish gates and
  receipt schema do not import or invoke S
- **AND WHEN** exact A3 is published and remote-reachable
- **THEN** only exact A3 integration paths may activate published S

#### Scenario: Authorization and dormant S use focused current proof
- **WHEN** publication eligibility is assessed for this source or future S
- **THEN** this docs-only source uses strict exact-object, reciprocal-relation,
  absence, ownership, JSON, TOML, current public-safety, source-classification,
  whitespace and manifest-scope checks, while future S uses focused static and
  connected POSIX proof
- **AND** neither payload executes, requires or accepts reachable-history,
  full-release, live execution, receipt, review, commit or push activity as
  publication evidence

#### Scenario: Child-supervisor authorization mismatch fails closed
- **WHEN** a card changes any rescue, authorization or successor id/path,
  adds a seventh source field, changes ceiling `500` or protocol `true`,
  creates future S before authorization publication, exceeds 499 added
  production LOC against the published authorization HEAD, expands S ownership
  or wires S before A3
- **THEN** deterministic verification rejects the source or candidate
- **AND** no malformed, partial or over-broad payload can authorize future S
