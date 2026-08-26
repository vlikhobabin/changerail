## ADDED Requirements

### Requirement: Affected v3 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v3` as one
docs-only authorization from exact published
`rescue-affected-release-profile-exact-target-proof-boundary` commit
`8772376bc3b3bbb5d9aa2dd96c5a47c9430a863d`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-target-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v3.md","successor_id":"implement-bounded-affected-release-profile-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-exact-target-proof-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v2`. It MUST block only
`implement-bounded-affected-release-profile-v3`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v3.md","authorization_id":"authorize-bounded-affected-release-profile-v3"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the four published predecessors above plus this published
authorization and block only `certify-accelerated-release-loop-v1`. Its card,
change and executable payload MUST remain absent until this authorization is
committed, reviewed, pushed and remotely reachable.

#### Scenario: Authorization leaves one bounded successor absent
- **WHEN** maintainers deliver or review this authorization
- **THEN** exact source object, dependencies, sole block and future reference are machine-checkable
- **AND** the implementation successor remains absent until publication.

### Requirement: Affected v3 authorization MUST preserve the exact target/proof boundary
The future implementation MUST preserve without weakening exact 35-ID digest,
complete 35→30 physical resolution, bounded aggregate NUL selection, exact
one-byte A/M/D and R/C plus three ASCII digits `000..100`, old+new operands,
sole scheduler v1 activation and full-only authority.

The closed target descriptor inventory MUST map each frozen command token
exactly once as effective-PATH executable, repository input file, repository
input directory or runtime output. Unknown, duplicate, missing, ambiguous,
unavailable, wrong-type/access or root-escaping targets MUST fail aggregate
admission with zero semantic launch before Git selection and semantics.

Scheduler summary jobs MUST be exact JSON integer `1` or `4`, never boolean,
float, string or null. Every published summary field/status/order/size and exact
pass, terminal, outer and synthetic row tuple MUST remain mandatory. Requested
affected MUST remain non-authoritative; only admitted exact full pass MAY
authorize. No receipt, capture, marker or cache may be created or accepted.

The literal four-step canonical-CI schema and finite exhaustive connected
counterfactual matrix MUST cover every selector stream/bound/fault, target kind/
mapping/root/type/access fault, scheduler typed cross-field/jobs mutation and CI
field/name/trigger/action/with/run/env/matrix/gating/direct/chained/wrapped/
indirect surface. Each fixture MUST be non-noop and fail when its production
guard is removed or weakened. Terminal unpublished v2 payload and evidence MUST
NOT be copied, cherry-picked or accepted.

#### Scenario: Authorization cannot narrow published proof
- **WHEN** the future implementation plans or verifies its trust boundary
- **THEN** every exact target, report, CI, selector, admission and authority invariant remains mandatory
- **AND** no terminal unpublished payload or evidence can satisfy it.

### Requirement: Affected v3 authorization MUST remain docs-only
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
