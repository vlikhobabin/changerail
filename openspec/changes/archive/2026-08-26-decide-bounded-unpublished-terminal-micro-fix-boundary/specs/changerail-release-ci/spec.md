## ADDED Requirements

### Requirement: Published bounded terminal micro-fix decision MUST precede v3 authorization
ChangeRail MUST publish
`decide-bounded-unpublished-terminal-micro-fix-boundary` as one clean tracked
`4.done` board card after the published psutil S2 decision and authorization,
and before creating either
`authorize-bounded-psutil-supervisor-micro-fix-v3` or
`deliver-psutil-backed-release-child-supervisor-v3`.

The decision MUST block both future cards. Its later authorization MUST depend
on this decision and block only the exact v3 successor. The v3 successor MUST
depend on both sources and use only this exact two-field inline JSON reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}
```

The future authorization MUST contain exactly one object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`:

```json
{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

#### Scenario: Decision retains exact v3 lineage without creating it
- **WHEN** maintainers deliver this decision before v3 publication
- **THEN** it blocks the exact authorization and successor, while the future
  authorization depends on the decision and blocks only the successor
- **AND** the successor depends on both cards and uses only its exact two-field
  authorization reference
- **AND** neither future card or executable payload exists in the decision
  delivery.

### Requirement: v3 micro-fix MUST be a clean bounded reconstruction
ChangeRail MUST permit the sole future v3 micro-fix only when its candidate is
unpublished, the exact published authorization is valid, all prior findings
are independently closed, and the latest cycle introduces exactly one new
isolated blocker. It MUST start from the clean HEAD that publishes its own
authorization, remain within the same authorized production paths and at most
499 added production LOC against that HEAD, and MUST NOT expand scope,
dependencies, schema or ownership.

The candidate may mechanically reconstruct executable code and tests from a
frozen failed candidate solely as source material. It MUST NOT reuse terminal
verdict, review history, log, receipt, manifest or evidence, and MUST rerun
every connected R1-R7 proof. It MUST receive exactly one implementation attempt
and one fresh Sol/high review; repair/retry/rescue budget is `0/0/0`. It MUST
NOT gain credential, mutation, live-admission or final authority.

#### Scenario: Reused terminal material cannot admit v3
- **WHEN** a proposed v3 candidate lacks a clean authorization start, exact
  authorization, independently closed prior findings, one isolated new latest
  blocker, fresh R1-R7 proof, unchanged authorized paths/scope or its LOC
  limit
- **THEN** ChangeRail rejects the candidate before review or publication
- **AND** verdict, history, log, receipt, manifest and other terminal evidence
  cannot substitute for the missing fresh proof.

### Requirement: R7 MUST distinguish pipe EOF from execution completion
The v3 micro-fix MUST treat pipe EOF only as stream state. It MUST NOT report
completion while the leader is live. Completion requires observing a terminal
leader state or reaching `execution_timeout`; cleanup MUST run only after that
completion condition. The connected R1-R7 proof MUST freshly cover EOF with a
live leader, observed terminal leader state, execution timeout and cleanup
order.

#### Scenario: Live leader after EOF remains incomplete
- **WHEN** the supervised pipe reaches EOF while the leader remains live
- **THEN** the v3 candidate does not report completion or successful cleanup
- **AND** it waits for a terminal leader observation or execution timeout,
  then performs cleanup under its existing bounded cleanup contract.

### Requirement: v3 and downstream refresh MUST remain dormant before publication
Before v3 publication, ChangeRail MUST keep S3 structurally dormant and MUST
block downstream refresh. The decision, future authorization and successor
MUST NOT create credential, mutation, live or final authority, or activate
release baseline, CI, review/publish gate, receipt schema or production
entrypoint outside the exact existing authorized scope.

#### Scenario: Decision delivery cannot activate S3
- **WHEN** maintainers fast-forward or deliver this docs-only decision
- **THEN** production, test and runtime LOC remain zero, the future
  authorization and successor cards/code remain absent, and downstream refresh
  stays blocked pending S3 publication
- **AND** history, full release baseline, live execution, review, commit and
  push are neither run nor accepted as decision evidence.
