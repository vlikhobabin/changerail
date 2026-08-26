## ADDED Requirements

### Requirement: Affected v4 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v4` as one
docs-only authorization from exact published
`rescue-affected-release-profile-proof-connectivity-boundary` commit
`63be8754ed6deb474d1c91dab3e931d28e7f37d3`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md","investigation_id":"rescue-affected-release-profile-proof-connectivity-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v4.md","successor_id":"implement-bounded-affected-release-profile-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-proof-connectivity-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v3`. It MUST block only
`implement-bounded-affected-release-profile-v4`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md","authorization_id":"authorize-bounded-affected-release-profile-v4"}
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

### Requirement: Affected v4 authorization MUST preserve connected resolved-base proof
The future implementation MUST preserve every resolved-base validation guard:
spawn/error, return code, stderr, timeout, exact one-newline framing, exact
40/64-byte lowercase hexadecimal OID, upper/non-hex/short/long/multiple or
missing newline, trailing bytes and non-ancestor after valid resolution.

Each guard MUST have a finite named connected fixture and an independent
counterfactual that removes or weakens only that guard. The focused gate MUST
fail when the intended condition is absent; an earlier-branch, digest-shielded,
tautological or unrelated mutation MUST NOT count.

#### Scenario: Authorization cannot accept disconnected base proof
- **WHEN** future v4 weakens or removes any resolved-base guard
- **THEN** its named focused counterfactual fails
- **AND** production selection still expands to all 35 IDs.

### Requirement: Affected v4 authorization MUST preserve protocol non-authority proof
The future implementation MUST create and accept no receipt, capture, marker or
cache. Its connected proof MUST start independently from affected subset,
affected full fallback, admission failure, scheduler failure and malformed
scheduler-summary controls, each non-authoritative before adding an artifact.

For every control and artifact class, add, forge and replay fixtures MUST prove
exact authority, status, selection/results and semantic-start parity with the
artifact-free control. Reports MUST expose no protocol field and execution MUST
not read, accept, create or update protocol state. One explicit mutant that
OR-upgrades authority from artifact presence MUST make the focused gate fail.

#### Scenario: Authorization cannot infer authority from an artifact
- **WHEN** a receipt, capture, marker or cache exists around a non-authoritative run
- **THEN** the result remains exactly as non-authoritative as its control
- **AND** an artifact-presence authority mutant is rejected.

### Requirement: Affected v4 authorization MUST preserve the exact v3 runtime floor
The future implementation MUST preserve exact 35-ID digest and 35→30 ownership,
bounded aggregate admission before selection, strict four-stream Git parsing
and bounds, typed scheduler summary rows/jobs, full-only authority and exact
source-safe four-step CI. Every v3 fixture that closed cycle-1 review findings
MUST remain active; terminal unpublished v3 payload and evidence MUST NOT be
copied, cherry-picked or accepted.

This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
dependencies, schemas, code, CI, baseline, receipt or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
execution/benchmark, live matrix, certification or terminal prototype evidence.
It requires one fresh Sol/high review and permits one same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization
- **THEN** only exact lineage and future constraints change
- **AND** selector, scheduler, history, full, affected, live and certification work remains absent.
