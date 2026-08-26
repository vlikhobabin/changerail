## ADDED Requirements

### Requirement: Published connected broker v5 authorization MUST bind exact proof
ChangeRail MUST publish `authorize-bounded-connected-broker-supervisor-v5` as
one clean tracked `4.done` docs-only card after published
`decide-connected-broker-supervisor-proof-boundary` and before creating
`deliver-connected-broker-supervisor-v5`.

The authorization MUST depend on the decision and block only exact v5. It MUST
contain exactly one object with only these six fields in this order and with
these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future v5 implementation MUST depend on both published sources and use
only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

It MUST start from the exact HEAD that publishes this authorization, add at
most 499 production LOC and add no dependency. It MUST reconstruct code and
tests from published requirements and generic findings only; terminal v4 code,
card, verdict, history, logs, manifest and evidence MUST NOT be copied or
accepted.

V5 MUST execute R8 fatal/timeout cleanup and R9 post-identity pidfd signaling
through public `supervise`. Disposable effective source mutations MUST remove
the public outer cleanup wiring and replace pidfd signaling with PID-only
signaling; each identical connected scenario MUST turn red. Direct private
helper calls, rejection before signaling and no-op/ambiguous mutations MUST NOT
satisfy the proof. Fresh bounded canonical and counterfactual evidence MUST be
retained for the v5 payload.

V5 receives exactly one implementation attempt and one fresh Sol/high review
with repair/retry/rescue budget `0/0/0`. It remains dormant outside focused
tests and cannot activate release baseline, CI, receipts, review/publish or
downstream work.

#### Scenario: Exact authorization leaves v5 absent
- **WHEN** maintainers deliver this authorization
- **THEN** exact object, reciprocal lineage, future reference, clean-start,
  LOC, proof and review boundaries remain machine-checkable
- **AND** successor card/code, executable activation, history, full baseline
  and live matrix evidence remain absent.

#### Scenario: Disconnected proof cannot satisfy authorization
- **WHEN** a future candidate calls private cleanup directly, rejects before
  signaling, omits either effective mutation or reuses v4 evidence
- **THEN** ChangeRail rejects it before publication
- **AND** the zero-repair budget does not authorize retry or rescue.

### Requirement: Connected broker v5 authorization MUST remain docs-only
This authorization delivery MUST modify only its card, same-slug OpenSpec
artifacts, synchronized release-CI specification and archive metadata.
Production, test and runtime LOC MUST remain zero. It MUST NOT create the
successor, dependency changes, schema, executable code, CI, baseline, receipt,
review/publish activation or retained runtime evidence.

#### Scenario: Authorization cannot execute v5
- **WHEN** maintainers plan, deliver, review or publish this authorization
- **THEN** no broker, target, history scan, full baseline or live matrix is
  started or accepted as authorization evidence.
