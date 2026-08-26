## ADDED Requirements

### Requirement: Proof-connectivity rescue MUST replace terminal unpublished affected v3
ChangeRail MUST publish
`rescue-affected-release-profile-proof-connectivity-boundary` as one docs-only
decision from exact published `authorize-bounded-affected-release-profile-v3`
tip `4203d1df3cdbe8b9f62bc6f30208b18d6860732e`.

The unpublished `implement-bounded-affected-release-profile-v3` path MUST be
terminal, non-conforming and forensic-only. Its payload, card, manifest,
verdicts, logs and evidence MUST NOT satisfy any dependency, authorization,
implementation, review or publication gate. Published cards and archives MUST
remain unchanged. After this decision is published the v3 implementation
successor MUST be exhausted and superseded by the exclusive v4 lineage.

The only conforming order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v4`, clean
`implement-bounded-affected-release-profile-v4`, then
`certify-accelerated-release-loop-v1`. The v4 authorization MUST contain exactly
one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md","investigation_id":"rescue-affected-release-profile-proof-connectivity-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v4.md","successor_id":"implement-bounded-affected-release-profile-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-proof-connectivity-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v3`. It MUST block only
`implement-bounded-affected-release-profile-v4`.

The v4 implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md","authorization_id":"authorize-bounded-affected-release-profile-v4"}
```

It MUST depend exactly on those four published predecessors plus published v4
authorization, block only `certify-accelerated-release-loop-v1`, start from the
authorization-publishing HEAD, add at most 499 production LOC and reconstruct
from published sources without copying or cherry-picking terminal work.

#### Scenario: Rescue leaves one published-source successor path
- **WHEN** maintainers publish this decision
- **THEN** unpublished v3 is exhausted and exact v4 lineage is exclusive
- **AND** authorization, implementation and certification successors remain absent.

### Requirement: Affected v4 MUST connect every resolved-base guard to proof
V4 MUST preserve the exact v3 profile, admission, selector and fallback behavior.
Focused proof MUST reach resolved-base validation with an otherwise valid probe
and independently cover spawn/error, return code, stderr, timeout, exact one
newline, exact 40/64-byte lowercase hexadecimal OID, uppercase/non-hex,
short/long, missing/multiple newline, trailing bytes and non-ancestor after a
valid resolved OID.

For every validation condition, a finite counterfactual MUST remove or weaken
only that guard and MUST make at least one named connected fixture fail. A
fixture that exits at an earlier branch, mutates only the expected profile hash,
or passes after the intended guard is removed MUST NOT count.

#### Scenario: Base guard removal is observable
- **WHEN** any resolved-base validation guard is removed or weakened
- **THEN** its named counterfactual fixture fails
- **AND** production selection still fails closed to all 35 IDs.

### Requirement: Affected v4 MUST prove protocol artifacts cannot create authority
V4 MUST create and accept no receipt, capture, marker or cache. Connected
fixtures MUST begin independently from affected subset, affected full fallback,
admission failure, scheduler failure and malformed scheduler summary states,
each already non-authoritative without an artifact.

For each state and each artifact class, fixtures MUST add, forge and replay a
disposable artifact and prove exact control parity for authority, status,
selection/results and semantic-start counts. Reports MUST contain no protocol
field and execution MUST neither read, accept, create nor update an artifact.
One explicit counterfactual that OR-upgrades authority when any artifact exists
MUST make the focused gate fail.

#### Scenario: Artifact cannot upgrade a non-authoritative result
- **WHEN** receipt, capture, marker or cache is added, forged or replayed around any non-authoritative state
- **THEN** authority and report semantics remain byte-for-byte equivalent to the artifact-free control
- **AND** an artifact-presence authority mutant is rejected.

### Requirement: Proof-connectivity rescue MUST preserve the closed v3 floor
V4 MUST preserve exact 35→30 ownership, aggregate admission before selection,
strict bounded four-stream Git parsing, typed scheduler rows/jobs, full-only
authority and exact source-safe four-step CI. Its proof MUST retain every v3
connected fixture that closed cycle-1 findings and MUST add the two v4 mutation
oracles without accepting unpublished v3 results as evidence.

This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
code, dependencies, schemas, CI or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
execution/benchmark, live matrix, certification or unpublished prototype
evidence. One fresh Sol/high review and one same-card docs repair are available.

#### Scenario: Decision cannot claim executable closure
- **WHEN** this decision is delivered or reviewed
- **THEN** only lineage and exact future proof boundaries change
- **AND** executable closure remains absent until separately published v4 work.
