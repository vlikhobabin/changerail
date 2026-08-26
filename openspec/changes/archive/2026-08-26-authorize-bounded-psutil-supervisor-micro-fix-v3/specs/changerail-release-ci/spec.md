## ADDED Requirements

### Requirement: Published bounded v3 micro-fix authorization MUST preserve the exact reconstruction boundary
ChangeRail MUST publish `authorize-bounded-psutil-supervisor-micro-fix-v3` as
one clean tracked `4.done` authorization card only after
`decide-bounded-unpublished-terminal-micro-fix-boundary`. The authorization
MUST contain exactly one object with only `investigation_card`,
`investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`, in this
exact order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The authorization MUST depend on that decision and block only the exact v3
successor. The future successor MUST depend on both sources and use only this
exact two-field inline JSON reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}
```

The successor MUST remain absent while this authorization is delivered. If it
is later created, it MUST be eligible only for an unpublished candidate with
this exact valid published authorization, independently closed prior findings
and exactly one new isolated latest blocker. It MUST start from the clean HEAD
that publishes this authorization, remain in the exact authorized production
paths, add at most 499 production LOC relative to that HEAD, and MUST NOT
expand scope, dependencies, schema or ownership.

The successor MAY mechanically reconstruct executable code and tests from the
frozen failed candidate solely as source material. It MUST NOT reuse terminal
verdict, review history, log, receipt, manifest or other evidence, and MUST
rerun every connected R1-R7 proof. It MUST treat pipe EOF as stream state only:
while the leader is live, EOF MUST NOT report completion. Completion requires a
terminal leader observation or `execution_timeout`, followed by cleanup under
the existing bounded cleanup contract.

The successor MUST receive exactly one implementation attempt and one fresh
Sol/high review, with repair/retry/rescue budget `0/0/0`; it MUST NOT gain
credential, mutation, live-admission or final authority. S3 and downstream
refresh MUST remain dormant until S3 publication. This authorization delivery
MUST add production, test and runtime LOC `0`, and MUST NOT create successor
card/code or run or accept history, full release baseline, live execution,
review, commit or push evidence.

#### Scenario: Exact authorization leaves the S3 successor dormant
- **WHEN** maintainers fast-forward or deliver the exact v3 authorization
- **THEN** the one ordered six-field object, reciprocal decision/authorization/
  future-successor lineage and exact two-field future reference are retained
- **AND** successor card/code remains absent, production, test and runtime LOC
  remain zero, and downstream refresh remains blocked pending S3 publication.

#### Scenario: Terminal material cannot substitute for a fresh v3 proof
- **WHEN** a proposed S3 successor lacks clean authorization provenance, exact
  eligibility, unchanged authorized scope, fresh connected R1-R7 proof or the
  required EOF/leader completion behavior
- **THEN** ChangeRail MUST reject it before review or publication
- **AND** frozen terminal verdicts, histories, logs, receipts, manifests and
  evidence MUST NOT substitute for the missing fresh proof.
