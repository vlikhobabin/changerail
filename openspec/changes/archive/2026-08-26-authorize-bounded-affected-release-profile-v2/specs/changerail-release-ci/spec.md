## ADDED Requirements

### Requirement: Affected v2 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v2` as one
docs-only authorization from exact published
`rescue-affected-release-profile-exact-report-proof-boundary` commit
`64ba9ab5c3af79c3babc4800969a68eae20ec5bb`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-report-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-report-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v2.md","successor_id":"implement-bounded-affected-release-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-exact-report-proof-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v1`. It MUST block only
`implement-bounded-affected-release-profile-v2`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v2.md","authorization_id":"authorize-bounded-affected-release-profile-v2"}
```

It MUST start from the authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the four published predecessors above plus this published
authorization and block only `certify-accelerated-release-loop-v1`. Its card,
change and executable payload MUST remain absent until this authorization is
committed, reviewed, pushed and remotely reachable.

#### Scenario: Authorization leaves one bounded successor absent
- **WHEN** maintainers deliver or review this authorization
- **THEN** exact source object, dependencies, sole block and future reference are machine-checkable
- **AND** the implementation successor remains absent until publication.

### Requirement: Affected v2 authorization MUST preserve the exact trust boundary
The future implementation MUST preserve without weakening the published
decision's exact 35-ID registry/digest, complete 35→30 physical resolution,
bounded aggregate NUL Git selector, rename/copy old+new operands, complete
aggregate effective-PATH admission before selection and semantics, sole
scheduler v1 activation and full-only authority.

It MUST validate scheduler summary status exactly `pass` iff all rows pass and
exactly `fail` otherwise; every terminal, outer and synthetic row MUST have
status `fail` and its exact published reason/cross-field tuple. It MUST create
and accept no receipt, capture, marker or cache. Affected/focused output and
forged/replayed protocol artifacts MUST NOT satisfy review, publish or
certification authority.

It MUST preserve the literal canonical-CI top-level/job/trigger/permission/
action/with/run/field/order schema and the exhaustive connected mutation floor
for scheduler rows/summaries, protocol artifacts, CI surfaces, Git selector,
admission zero-launch and full-only authority. Terminal unpublished v1 or prior
rescue code, cards, manifests, verdicts, logs and evidence MUST NOT be copied,
cherry-picked or accepted.

#### Scenario: Authorization cannot narrow published proof
- **WHEN** the future implementation plans or verifies its trust boundary
- **THEN** every exact report, protocol, CI, selector, admission and authority invariant remains mandatory
- **AND** no terminal unpublished payload or evidence can satisfy it.

### Requirement: Affected v2 authorization MUST remain docs-only
This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
dependencies, schemas, code, CI, baseline, receipt or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
benchmark, live matrix, certification or terminal prototype evidence. It
requires one fresh Sol/high review and permits one same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization
- **THEN** only exact lineage and future constraints change
- **AND** selector, scheduler, history, full, affected, live and certification work remains absent.
