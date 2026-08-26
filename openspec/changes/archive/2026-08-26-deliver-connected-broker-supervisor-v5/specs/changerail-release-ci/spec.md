## ADDED Requirements

### Requirement: Connected broker supervisor v5 MUST satisfy its public-path proof
ChangeRail MUST allow `deliver-connected-broker-supervisor-v5` only from exact
published authorization HEAD `888f2aaeb5a5b352474c100c63c68f1de612a7a1`,
with this sole authorization reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

The implementation MUST add no dependency and at most 499 production LOC. It
MUST use one dedicated Linux broker subprocess that becomes subreaper before
target launch, owns only its target tree and communicates through a closed,
versioned, bounded ready/started/terminal protocol. Protocol faults, EOF,
overflow, timeout, broker loss and incomplete cleanup MUST fail closed.

Recoverable broker faults MUST clean exact owned descendants through bounded
TERM/KILL/reap and two empty scans. Identity-bound signals MUST use pidfds after
identity validation. Fatal controller paths MUST perform bounded outer broker
process-group cleanup without claiming coverage of detached sessions.

The focused proof MUST call public `supervise` for R8 fatal/timeout cleanup and
R9 post-identity pidfd signaling. It MUST execute identical scenarios against
effective disposable source mutations that remove public outer cleanup wiring
and replace pidfd signaling with PID-only signaling. Each mutation MUST be
unique, asserted and turn its connected scenario red. Direct private cleanup
calls, rejection before signaling, no-op/ambiguous mutations and terminal v4
evidence MUST NOT satisfy the proof.

V5 MUST retain fresh bounded canonical/counterfactual evidence, remain dormant
outside focused tests and receive exactly one Sol/high review with `0/0/0`
repair/retry/rescue budget.

#### Scenario: Canonical public path passes and counterfactuals fail
- **WHEN** maintainers execute the focused v5 proof
- **THEN** canonical public `supervise` proves outer cleanup and pidfd signaling
  with no owned survivor
- **AND** each exact disposable mutation demonstrably changes source and makes
  the identical public scenario fail for its intended missing connection.

#### Scenario: Disconnected or reused proof blocks publication
- **WHEN** either connected mutation is absent, ineffective or bypasses public
  `supervise`, or any v4 runtime evidence is reused
- **THEN** review returns NO-GO and the zero-repair v5 lineage terminates.

### Requirement: Connected broker v5 MUST remain dormant after delivery
The v5 delivery MUST NOT wire its module into release baseline, CI, receipts,
review/publish or downstream activation. It MUST NOT run or accept reachable
history, full release baseline or live matrix evidence.

#### Scenario: Focused delivery creates no activation
- **WHEN** maintainers implement, verify, review or publish v5
- **THEN** only its dormant module, focused test, card, OpenSpec artifacts and
  necessary metadata change
- **AND** production entrypoints and canonical release execution stay unchanged.
