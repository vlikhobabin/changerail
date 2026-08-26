## ADDED Requirements

### Requirement: Connected broker proof decision MUST precede v5 authorization
ChangeRail MUST publish `decide-connected-broker-supervisor-proof-boundary` as
one clean tracked `4.done` docs-only card after the published broker v4 decision
and authorization, and before creating either
`authorize-bounded-connected-broker-supervisor-v5` or
`deliver-connected-broker-supervisor-v5`.

The decision MUST block both future cards. The future authorization MUST depend
on this decision and block only the exact implementation. The future
implementation MUST depend on both and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

The future authorization alone MUST contain exactly one object with only these
six fields in this order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Publication of this decision MUST exhaust the unpublished v4 implementation
path. Published v4 sources remain immutable history but MUST NOT authorize v4
creation, continuation, repair, rescue, reuse or publication after this
decision. Exact v5 MUST be the sole conforming future broker-supervisor path.

#### Scenario: Decision creates no future authority or implementation
- **WHEN** maintainers deliver this decision
- **THEN** it retains the exact future objects and reciprocal lineage without
  creating either future card or executable payload
- **AND** v4 code, verdict, history, manifest, logs and evidence remain
  forensic-only and cannot authorize or satisfy v5.

### Requirement: V5 MUST prove outer cleanup through public supervise
The future v5 focused proof MUST invoke public `supervise` for fatal broker-loss
and outer-timeout scenarios. It MUST observe bounded terminal failure and prove
that no same-process-group target survives. It MUST NOT call `_stop_group`
directly as a substitute for the production connection.

The proof MUST execute the same scenario against a disposable source mutation
that removes the exact public-path `_stop_group(proc)` exception or timeout
wiring. It MUST verify that the mutation changed the intended construct and
that the connected scenario fails. A no-op, ambiguous or unexecuted mutation
MUST fail the proof.

#### Scenario: Removed supervise cleanup wiring turns proof red
- **WHEN** the disposable candidate removes the outer cleanup call used by
  public `supervise`
- **THEN** the identical public scenario detects the missing cleanup connection
  and fails
- **AND** direct helper invocation cannot make the counterfactual pass.

### Requirement: V5 MUST prove pidfd signaling after identity validation
The future v5 focused proof MUST invoke public `supervise`, pass exact identity
validation, reach the signaling operation and observe use of
`pidfd_send_signal`. PID-only `os.kill(pid, sig)` MUST NOT substitute for this
operation.

The proof MUST execute the same scenario against a disposable source mutation
that replaces the pidfd signal operation with PID-only signaling. It MUST
verify the intended mutation occurred and that the connected scenario fails on
the forbidden backend observation. Rejection before any signal is attempted is
insufficient.

#### Scenario: PID-only signaling turns proof red
- **WHEN** the disposable candidate replaces post-identity pidfd signaling with
  `os.kill(pid, sig)`
- **THEN** the public connected scenario reaches signaling, observes the
  forbidden backend and fails
- **AND** an earlier identity mismatch cannot satisfy this proof.

### Requirement: V5 MUST be a clean bounded one-review delivery
Future `deliver-connected-broker-supervisor-v5` MUST start from the exact HEAD
that publishes its authorization, use only the exact two-field reference, add
at most 499 production LOC and add no dependency. It MUST reconstruct code and
tests from published requirements and generic findings only; terminal v4 code,
card, verdict, history, logs, manifest and evidence MUST NOT be copied or
accepted.

V5 MUST retain bounded canonical and counterfactual command evidence for R8 and
R9, preserve the published broker ownership/protocol/cleanup contract and stay
dormant outside focused tests. It receives exactly one implementation attempt
and one fresh Sol/high review with repair/retry/rescue budget `0/0/0`.

#### Scenario: Missing connected counterfactual blocks v5
- **WHEN** a proposed v5 lacks clean authorization provenance, exact scope,
  canonical public-path proof, either effective counterfactual mutation,
  retained fresh evidence or the LOC/dependency boundary
- **THEN** ChangeRail rejects it before publication
- **AND** no repair, retry, rescue or terminal v4 evidence reuse is permitted.

### Requirement: Connected proof decision MUST remain docs-only and dormant
This decision delivery MUST add production, test and runtime LOC `0`, MUST NOT
create either future card or code, and MUST NOT activate release baseline, CI,
receipt, review/publish or downstream work. It MUST NOT run or accept reachable
history, full release baseline or live matrix evidence.

#### Scenario: Decision cannot execute v5 proof
- **WHEN** maintainers plan, deliver, review or publish this decision
- **THEN** only its card, same-slug artifacts, synchronized main spec and
  archive metadata change
- **AND** all executable and downstream surfaces remain unchanged.
