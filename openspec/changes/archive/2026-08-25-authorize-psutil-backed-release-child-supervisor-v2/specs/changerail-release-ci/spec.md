## ADDED Requirements

### Requirement: Published psutil-backed release child supervisor v2 authorization source
ChangeRail MUST publish `authorize-psutil-backed-release-child-supervisor-v2`
as one clean tracked `4.done` board card after published
`rescue-psutil-release-child-supervisor-boundary` and before creating
`implement-psutil-backed-release-child-supervisor-v2`. The source MUST contain
exactly one `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`:

```json
{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The authorization MUST depend on the published decision and block only the
exact future implementation. The decision MUST block both the authorization
and the implementation. The future implementation MUST depend on both sources,
use only exact inline JSON
`{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}`
as its published authorization reference, and remain at no more than 499 added
production LOC relative to the exact HEAD that publishes this authorization.

#### Scenario: S2 authorization binds only the exact future implementation
- **WHEN** maintainers publish the S2 authorization source
- **THEN** it contains only the exact six-field object, depends on the
  published S2 decision and blocks only the exact future implementation
- **AND** the decision blocks both future cards, while the future implementation
  depends on both and uses only its exact two-field published reference
- **AND** the published S v1 authorization and failed unpublished S2 material
  cannot authorize the replacement.

### Requirement: Authorized S2 keeps the bounded portable cleanup contract
Future `implement-psutil-backed-release-child-supervisor-v2` MUST pin
`psutil==7.1.0` in runtime, development, bootstrap and admission dependency
surfaces. It MUST use a bounded stdlib `selectors`/`prctl` adapter and MUST NOT
assume, require, write or derive authority from a writable cgroup. It MUST
accept distinct positive `execution_timeout` and `cleanup_timeout`; total
elapsed time MUST be at most
`execution_timeout + cleanup_timeout + 1.0s`, where `1.0s` is fixed setup and
report overhead only. Cleanup failure is terminal.

Every psutil error MUST fail closed. The implementation MUST identify every
process by exact `(pid, create_time)`. The inclusive maxima are 128 unique
identities, 128 descendants in each `children(recursive=True)` scan and 32
cleanup scans: exactly each maximum MUST remain permitted and only strict
`>128`, `>128` or `>32` excess is terminal. Recursive cleanup MUST report
success only at the second consecutive empty identity scan; zero or one empty
scan is not successful cleanup. Identity mismatch, timeout or cleanup error is
terminal.

#### Scenario: S2 rejects ambiguous, unbounded or premature cleanup
- **WHEN** S2 observes a psutil error, `(pid, create_time)` mismatch, timeout,
  cleanup failure, strict cap excess or fewer than two consecutive empty scans
- **THEN** it fails closed and does not report successful cleanup
- **AND** exactly 128 identities, 128 descendants and 32 scans remain allowed,
  while the second consecutive empty scan is the success threshold
- **AND** it does not compensate through writable cgroup authority or an
  extended total timeout budget.

### Requirement: Authorized S2 remains dormant pending downstream refresh
Before exact S2 publication, ChangeRail MUST keep the release baseline, CI
workflow, review/publish gate, receipt schema and production entrypoint from
importing, invoking or activating S2. H4, I3, W1, R3 and A3 authorization and
implementation work MUST remain blocked until exact S2 publication and a later
tracked refresh explicitly establishes their downstream authorization and
dependency relations.

The future proof matrix MUST connect static assertions for exact lineage,
four-surface pin, bounded selector/prctl and writable-cgroup absence, timeout
arithmetic, psutil error/identity/cap/stable-empty cleanup and dormant wiring
with downstream refresh blocking. This authorization and future S2 MUST NOT
use live execution, reachable history, full release baseline, review, commit
or push as required proof.

#### Scenario: Authorization does not activate S2 or downstream work
- **WHEN** this authorization is delivered before S2 publication
- **THEN** its payload contains only documentation authority artifacts,
  production, test and runtime additions remain zero, and the future successor
  card/code remain absent
- **AND** baseline and CI wiring stay absent, while downstream H4/I3/W1/R3/A3
  work remains blocked pending later publication and refresh.
