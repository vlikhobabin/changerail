## ADDED Requirements

### Requirement: Published scheduler authorization MUST bind exact dormant scope
ChangeRail MUST publish `authorize-bounded-release-semantic-scheduler-v1` as
one clean tracked `4.done` docs-only card after published
`decide-accelerated-release-loop-integration-boundary` commit
`0de81cf7e578335c728466b81c1c60b6d447dab7` and before creating
`implement-bounded-release-semantic-scheduler-v1`.

The authorization MUST depend on the decision, block only exact scheduler v1
and contain exactly one object with only these six fields in this order and
exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future implementation MUST depend on both published sources and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

It MUST start from the exact authorization-publishing HEAD, add at most 499
production LOC and import only published connected broker supervisor v5 for
child ownership. Terminal unpublished prototypes, cards, verdicts, manifests,
logs and evidence MUST NOT satisfy its implementation or review.

#### Scenario: Exact authorization leaves successor absent
- **WHEN** maintainers deliver this authorization
- **THEN** exact object, reciprocal lineage, future reference, clean-start and
  LOC boundaries remain machine-checkable
- **AND** successor card/code, executable activation and expensive evidence
  remain absent.

### Requirement: Scheduler authorization MUST freeze bounded execution contract
Future scheduler v1 MUST prevalidate one immutable plan of 1..64 unique task
IDs, commands, timeouts and isolated roots before launching any child. It MUST
accept jobs 1..4, execute each task exactly once through published v5, cancel
outstanding tasks on terminal failure and emit exactly one deterministic
registry-ordered result per task.

Every child MUST retain v5's 8192-byte combined-output cap. The scheduler
summary MUST be at most 64 KiB and MUST contain no raw child output. Malformed,
duplicate, missing, unknown, incomplete or over-bound task/result state MUST
fail closed.

Scheduler MUST NOT own Git selection, semantic inventory, release profiles,
runner/CI activation, receipts, review/publish or authority. It MUST remain
structurally dormant outside focused tests until exact later affected-profile
implementation activates it.

#### Scenario: Future scheduler proves jobs parity and cancellation
- **WHEN** focused scheduler proof executes independent tasks with jobs 1 and
  default jobs up to 4
- **THEN** results have identical exact-once registry order and bounded schema
- **AND** prelaunch, failure, timeout, output, malformed-result and descendant
  fixtures fail closed without an owned survivor.

#### Scenario: Unauthorized activation blocks successor
- **WHEN** a future scheduler candidate imports into baseline, CI, receipt,
  review/publish or another production entrypoint
- **THEN** structural dormancy proof and review fail
- **AND** the authorization cannot be used to widen that scope.

### Requirement: Scheduler authorization MUST remain docs-only
This authorization delivery MUST modify only its card, same-slug OpenSpec
artifacts, synchronized `changerail-release-ci` specification and archive
metadata. Production, test and runtime LOC MUST remain 0. It MUST NOT create
the successor, dependency changes, schemas, executable code, CI, baseline,
receipt, review/publish activation or retained runtime evidence.

It MUST NOT run or accept reachable-history, full release baseline or live
matrix evidence. It receives one fresh Sol/high review with one same-card docs
repair available.

#### Scenario: Authorization cannot execute scheduler work
- **WHEN** maintainers plan, deliver, review or publish this authorization
- **THEN** only exact authorization and bounded future contracts change
- **AND** no scheduler, semantic task, history scan, full baseline or live
  matrix is started or accepted.
