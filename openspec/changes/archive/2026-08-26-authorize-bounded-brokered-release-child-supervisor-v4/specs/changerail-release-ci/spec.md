## ADDED Requirements

### Requirement: Published brokered v4 authorization MUST bind only exact v4
ChangeRail MUST publish
`authorize-bounded-brokered-release-child-supervisor-v4` as one clean tracked
`4.done` docs-only card after published
`decide-brokered-release-child-supervision-boundary` and before creating
`deliver-brokered-release-child-supervisor-v4`.

The authorization MUST depend on the exact decision and block only exact v4.
It MUST contain exactly one object with only the following six fields in this
order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future implementation MUST depend on both published sources and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}
```

It MUST start from the exact HEAD that publishes this authorization, add at
most 499 production LOC, add no external dependency beyond the published
psutil pin, and implement the complete broker ownership, protocol, cleanup,
fatal-death honesty and proof boundary from the decision. It receives one
initial Sol/high review, at most one bounded same-card repair and one final
Sol/high re-review. Any surviving blocker is terminal.

The earlier v3 executable path MUST remain exhausted. Published v3 sources are
immutable history but MUST NOT authorize implementation work. Exact v4 and all
downstream activation MUST remain dormant until v4 publication and a later
tracked refresh.

#### Scenario: Authorization leaves exact v4 absent and dormant
- **WHEN** maintainers deliver this authorization
- **THEN** its exact six-field object, reciprocal lineage, future two-field
  reference, clean-start/LOC/proof/review boundaries and v3 exhaustion remain
  machine-checkable
- **AND** future v4 card/code, executable activation, downstream refresh,
  history, full baseline and live matrix evidence remain absent.

### Requirement: Brokered v4 authorization delivery MUST remain docs-only
The authorization delivery MUST modify only its card, same-slug OpenSpec
artifacts, synchronized `changerail-release-ci` specification and archive
metadata. Production, test and runtime LOC MUST remain zero. It MUST NOT create
the successor, dependency changes, protocol schema, executable code, CI,
baseline, receipt, review/publish activation or retained runtime evidence.

#### Scenario: Docs-only authority does not execute the future protocol
- **WHEN** the authorization is planned, delivered, reviewed or published
- **THEN** no broker process, target process, history scan, full baseline or
  live matrix is started or accepted as authorization evidence.
