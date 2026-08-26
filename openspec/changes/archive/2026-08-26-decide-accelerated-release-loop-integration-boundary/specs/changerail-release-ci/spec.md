## ADDED Requirements

### Requirement: Accelerated loop decision MUST split scheduler and activation
ChangeRail MUST publish
`decide-accelerated-release-loop-integration-boundary` as one clean tracked
`4.done` docs-only card after published
`deliver-connected-broker-supervisor-v5` commit
`9872d4edd5c35eb51d64d1199000c029f11bd92d` and before creating any future
scheduler, affected-profile or certification card.

The decision MUST block exact scheduler authorization and implementation,
affected-profile authorization and implementation, and final certification.
The only conforming publication order MUST be decision, scheduler
authorization, scheduler implementation, affected authorization, affected
implementation and certification. Every predecessor MUST be published and
remotely reachable before the next card is created.

#### Scenario: Decision leaves all successors absent
- **WHEN** maintainers deliver this decision
- **THEN** exact lineage and ordering are retained without creating a future
  card or executable payload
- **AND** private prototypes and terminal unpublished candidates remain
  forensic-only and cannot satisfy any dependency or evidence gate.

### Requirement: Scheduler authorization MUST bind dormant bounded execution
Future `authorize-bounded-release-semantic-scheduler-v1` MUST depend on this
published decision and block only exact
`implement-bounded-release-semantic-scheduler-v1`. The authorization alone MUST
contain exactly one object with only these six fields in this order and exact
values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation MUST depend on both published sources and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

It MUST start from the exact authorization-publishing HEAD, add at most 499
production LOC and import only published connected broker v5 for child process
ownership. It MUST prevalidate one immutable plan of 1..64 unique task IDs,
commands, timeouts and isolated roots before launch; accept jobs 1..4; execute
each task exactly once; cancel outstanding work after terminal failure; and
emit one deterministic registry-ordered result per task.

Every child MUST retain v5's 8192-byte combined-output cap. Scheduler summary
MUST be at most 64 KiB and MUST NOT contain raw child output. Malformed,
duplicate, unknown, missing, over-bound or incomplete task/result state MUST
fail closed.

Scheduler v1 MUST NOT own Git selection, release profiles, semantic inventory,
runner/CI activation, receipts, review/publish or authority. It MUST remain
dormant outside focused tests until exact affected-profile implementation.

#### Scenario: Dormant scheduler proves bounded ordered execution
- **WHEN** future scheduler v1 receives valid independent tasks with jobs 1 and
  default jobs up to 4
- **THEN** it executes each task exactly once through v5 and returns identical
  deterministic ordered results
- **AND** connected fault fixtures prove prelaunch rejection, failure
  cancellation, timeout/output bounds and no owned survivor.

#### Scenario: Scheduler cannot activate itself
- **WHEN** scheduler authorization or implementation is delivered
- **THEN** repository-wide wiring proof finds no baseline, CI, receipt,
  review/publish or other production activation
- **AND** history, full baseline and live matrix evidence are not run or
  accepted.

### Requirement: Affected authorization MUST own selection and sole activation
Future `authorize-bounded-affected-release-profile-v1` MUST be created only
after published scheduler v1, depend on this decision and that implementation,
and block only exact `implement-bounded-affected-release-profile-v1`. The
authorization alone MUST contain exactly one object with only these six fields
in this order and exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation MUST depend on all published predecessors and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

It MUST start from the exact authorization-publishing HEAD and add at most 499
production LOC. It MUST own the canonical semantic inventory, exact physical
resolution, bounded NUL Git selector and the sole runner import/activation of
scheduler v1. It MUST NOT redefine v5 or scheduler supervision, cleanup or
result contracts.

Zero arguments MUST remain the compatibility alias for requested
`full-release`; explicit `--profile full-release` MUST be identical. Requested
`affected` MUST require exactly one `--base`; invalid or repeated combinations
MUST fail before admission or semantic launch.

Selection MUST aggregate committed, staged, unstaged and untracked paths and
retain rename/copy old and new operands. Invalid or non-ancestor base, unknown
status, malformed framing, absolute/traversal/control path, unknown or
ambiguous ownership, selector/authority self-change, Git nonzero/stderr/timeout
or any declared path/count/byte bound breach MUST deterministically select the
full semantic inventory with a fallback reason.

#### Scenario: Known paths select bounded required semantics
- **WHEN** affected mode receives valid docs-only or owned-Python changes
- **THEN** selection includes the invariant safety floor and every exact
  functional owner with deterministic deduplication and order
- **AND** scheduler executes only that resolved plan once.

#### Scenario: Uncertainty falls back without authority
- **WHEN** selector input is unknown, ambiguous, self-referential, malformed or
  over bound
- **THEN** affected mode selects the exact full semantic inventory and records
  its deterministic fallback reason
- **AND** requested affected remains non-authoritative.

### Requirement: Full release MUST remain the only authoritative profile
Requested profile MUST determine authority. Every requested `affected` result
MUST report `authoritative:false`, including exact full fallback and successful
execution. Only an admitted requested `full-release` that executes and passes
the exact full semantic inventory MAY report `authoritative:true`.

Canonical CI MUST contain exactly one active explicit full runner and MUST NOT
invoke affected mode, scheduler, broker or individual semantic commands
directly. Parsed YAML and Python AST ownership proof MUST reject inactive,
duplicate, chained, wrapped, indirect, reordered or additional execution
surfaces.

Review, publish, receipt and certification gates MUST reject affected output,
timing, fallback or selected-result JSON as full-release evidence.

#### Scenario: Affected success cannot authorize publish
- **WHEN** requested affected execution passes a subset or its full fallback
- **THEN** the result remains diagnostic and non-authoritative
- **AND** review, publish and receipt gates cannot accept it as full evidence.

#### Scenario: Canonical CI executes only full release
- **WHEN** maintainers validate the release workflow
- **THEN** one active exact full-release runner owns all semantic execution
- **AND** any affected or alternate direct execution path makes the parsed
  ownership oracle fail.

### Requirement: Final certification MUST be single-shot and evidence-only
`certify-accelerated-release-loop-v1` MUST be created only after both exact
implementations are published and remotely reachable. It MUST change
production, test and runtime LOC 0 and MUST be the sole card in this lineage
that may run reachable-history or full-release evidence.

Certification MUST first obtain one fresh critical Sol/xhigh pre-capture audit.
On GO it MUST run exactly one reachable-history scan and exactly one requested
full-release baseline with retry/repair/rescue budget `0/0/0`. It MUST also run
one disposable clean docs-only affected scenario, one owned-Python affected
scenario and one unknown-path full fallback.

Docs-only MUST finish within 15 seconds and select at most 15 semantic IDs.
Owned Python MUST finish within 120 seconds. Unknown input MUST select the
exact full semantic inventory and remain non-authoritative. Timing MUST be
monotonic diagnostic evidence and MUST NOT affect selection, pass/fail,
authority, ordering, retry or receipt eligibility.

#### Scenario: Single-shot acceleration certification passes
- **WHEN** pre-capture audit is GO and the one allowed evidence sequence
  satisfies correctness, authority, parity and performance contracts
- **THEN** certification retains fingerprint-bound bounded evidence and may be
  published
- **AND** no second history or full execution is permitted.

#### Scenario: Failed measurement cannot be repaired in certification
- **WHEN** any history, full, affected, fallback, timing, RSS, freshness or
  authority assertion fails
- **THEN** certification terminates without production repair or evidence retry
- **AND** any redesign requires a new investigation.

### Requirement: Integration decision MUST remain docs-only and dormant
This decision delivery MUST add production, test and runtime LOC 0 and modify
only its card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` specification and archive metadata. It MUST NOT create
future cards, code, dependencies, schemas, runner/CI wiring, receipts or
review/publish activation.

It MUST NOT run or accept reachable-history, full release baseline, live matrix
or private prototype evidence. It receives one fresh Sol/high review with one
same-card docs repair available.

#### Scenario: Decision cannot claim implementation acceleration
- **WHEN** maintainers plan, deliver, review or publish this decision
- **THEN** only exact lineage, ownership, order, limits and certification
  contracts change
- **AND** current release execution behavior remains unchanged.
