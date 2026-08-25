## ADDED Requirements

### Requirement: Published psutil-backed release child supervisor v2 decision
ChangeRail MUST publish
`rescue-psutil-release-child-supervisor-boundary` as a clean tracked `4.done`
decision after published `rescue-release-process-supervisor-boundary` and
`authorize-bounded-release-child-supervisor-v1`, before creating either
`authorize-psutil-backed-release-child-supervisor-v2` or
`implement-psutil-backed-release-child-supervisor-v2`. The decision MUST block
both future cards and retain exactly this future authorization object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`:

```json
{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The later authorization MUST depend on this decision and block only the exact
successor. The future implementation MUST depend on both the decision and the
authorization, use only exact inline JSON
`{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}`
as its published authorization reference, and remain at no more than 499 added
production LOC relative to the exact remote-reachable HEAD that publishes its
authorization.

#### Scenario: S2 lineage starts only from the new published decision
- **WHEN** maintainers prepare the psutil-backed S2 lineage
- **THEN** this decision blocks both future cards, the future authorization
  depends on the decision and blocks only the exact future implementation
- **AND** the future implementation depends on both cards and uses the exact
  two-field authorization reference
- **AND** the published S v1 authorization cannot authorize v2, while the
  failed unpublished S2 authorization attempt is not reusable.

### Requirement: Psutil-backed S2 uses bounded portable cleanup
Future `implement-psutil-backed-release-child-supervisor-v2` MUST pin
`psutil==7.1.0` in runtime, development, bootstrap and admission dependency
surfaces. It MUST use a bounded stdlib `selectors`/`prctl` adapter and MUST NOT
assume, require, write or derive authority from a writable cgroup. It MUST
accept distinct positive `execution_timeout` and `cleanup_timeout` values, and
its total elapsed budget MUST be at most
`execution_timeout + cleanup_timeout + 1.0s`; `1.0s` is fixed setup/report
overhead only. Cleanup failure is terminal.

Every psutil error MUST fail closed. The implementation MUST identify a process
by exact `(pid, create_time)`. The `128` unique-identity, `128` descendant-per-
`children(recursive=True)`-scan and `32` cleanup-scan caps are inclusive allowed
maxima: exactly 128/128/32 MUST remain permitted, and only a value greater than
the applicable cap is terminal. It MUST require exactly two consecutive
`children(recursive=True)` scans with empty identity sets before declaring
recursive cleanup successful; the second empty scan is the success threshold,
not a failure cap. Identity mismatch, strict cap excess, timeout or cleanup
error MUST be terminal.

#### Scenario: S2 cleanup rejects unbounded or ambiguous containment
- **WHEN** S2 observes a psutil error, `(pid, create_time)` mismatch, timeout,
  cleanup failure, more than 128 identities, more than 128 descendants in one
  scan or more than 32 scans
- **THEN** it terminates fail-closed and does not report successful cleanup
- **AND** it does not compensate by assuming a writable cgroup or extending the
  exact total timeout budget.

#### Scenario: Stable-empty success requires its second empty scan
- **WHEN** focused negative proof observes zero or one consecutive empty
  `children(recursive=True)` identity set, or observes more than 128 identities,
  more than 128 descendants in one scan or more than 32 cleanup scans
- **THEN** it rejects premature cleanup success for fewer than two empty scans
  and rejects only the strict `>128`/`>128`/`>32` cap excesses
- **AND** exactly 128 identities, 128 descendants in one scan and 32 cleanup
  scans remain allowed, while the second consecutive empty scan reports success.

### Requirement: S2 remains dormant pending publication and downstream refresh
Before exact S2 publication, ChangeRail MUST keep its release baseline, CI workflow, review/publish gate, receipt schema and production entrypoint from importing, invoking or activating S2.
H4, I3, W1, R3 and A3 authorization and implementation work MUST remain
blocked until exact S2 publication and a later tracked refresh explicitly
re-establishes their downstream authorization and dependency relations.

The future S2 proof matrix MUST connect static assertions for: exact
decision/authorization/successor lineage; pin presence in runtime, development,
bootstrap and admission; bounded selector/prctl scope and writable-cgroup
absence; separate timeout arithmetic; psutil error, identity, cap and
stable-empty cleanup; and dormant wiring plus downstream refresh blocking.
Neither this decision nor future S2 may use live execution, reachable history,
full release baseline, review, commit or push as required proof.

#### Scenario: No stale lineage activates S2 or downstream work
- **WHEN** S2 has not been published and a later H4/I3/W1/R3/A3 card is
  planned, implemented, reviewed or activated
- **THEN** deterministic checks reject the attempt until S2 publication and a
  later explicit refresh have established its exact dependency
- **AND** baseline and CI wiring remain absent throughout the dormant period.

### Requirement: Psutil-backed S2 decision delivery remains docs-only
`$changerail-ff` and `$changerail-do` for `rescue-psutil-release-child-supervisor-boundary` MUST create or update only
the same decision card, proposal, design, release-CI delta, tasks, synchronized
main specification and archive metadata. Production, test and runtime LOC MUST
remain zero; future authorization and successor cards/code MUST remain absent;
and only generic forensic summaries of unpublished paths may be tracked.

#### Scenario: Decision does not create authority payloads
- **WHEN** maintainers fast-forward or deliver this decision
- **THEN** no future authorization or implementation card, code, diff,
  evidence, local identifier, history scan, full baseline, live execution,
  review, commit or push is created or accepted as decision evidence.
