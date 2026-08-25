## ADDED Requirements

### Requirement: Tiered release authority MUST use a dormant A1 and authoritative A2 boundary
After publication of `rescue-tiered-release-authority-two-stage-boundary`, ChangeRail MUST NOT continue or publish the unpublished
`implement-tiered-release-authority-core` payload. Future release authority
delivery MUST use two clean, separately authorized successors: dormant passive
admission/registry library A1 and terminal authority activation A2. The only
decision sources for this rescue are published commits `25f756e` and
`0fba407`; failed Scope A code, tests, diff, evidence, receipts and runtime
state MUST remain forensic-only and MUST NOT be reused.

#### Scenario: A1 authorization binds only passive admission and registry
- **WHEN** maintainers publish
  `authorize-bounded-passive-release-admission-registry`
- **THEN** it contains exactly
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-authority-two-stage-boundary.md","investigation_id":"rescue-tiered-release-authority-two-stage-boundary","successor_card":"openspec/board/3.inprogress/implement-passive-release-admission-registry.md","successor_id":"implement-passive-release-admission-registry","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":false}`
- **AND** A1 is limited to `<=499` production LOC against the exact published
  A1 authorization HEAD and cannot claim protocol, credential, mutation, live
  or terminal release authority

#### Scenario: A1 owns exact bounded passive behavior
- **WHEN** `implement-passive-release-admission-registry` is scoped or reviewed
- **THEN** it exclusively owns the literal 35-record registry, canonical
  digest, owners, direct commands and sequential groups; total bounded injected
  admission; effective-PATH Python and parsed distribution-pin/Ruff-origin
  checks; offline OpenSpec admission; bounded Git added, modified, deleted,
  renamed, copied and untracked selection; the closed path map; and its parsed
  Python-AST ownership oracle
- **AND** missing, duplicate, unknown, malformed, ambiguous, over-limit or
  unavailable inputs fail closed through connected focused fault cases without
  starting an admitted semantic command

#### Scenario: A1 remains structurally dormant
- **WHEN** A1 is delivered, reviewed or published before separately published
  `implement-terminal-release-authority-activation`
- **THEN** no release baseline, CI workflow, manifest/review/publish preflight,
  receipt schema or production entrypoint imports, invokes or activates A1
- **AND WHEN** that exact A2 is published
- **THEN** only that exact A2 may import, invoke or activate published A1
- **AND** a static negative-wiring oracle becomes RED for every pre-A2 import,
  invocation, receipt authority or activation path and every post-A2 such path
  outside exact A2

#### Scenario: Dormant A1 uses focused proof without terminal capture
- **WHEN** A1 publication eligibility is assessed
- **THEN** its exclusive deterministic publication gate accepts only real
  offline admission plus focused, static and current-only deterministic checks,
  followed by fresh independent Sol/`xhigh` review
- **AND** A1 MUST NOT execute, require or accept a reachable-history scan, full
  release baseline, authority receipt or terminal capture as publication
  evidence
- **AND** those prohibited authority checks cannot be cited as a reusable
  full-release pass or publication authority for A2

#### Scenario: A2 authorization binds only terminal activation
- **WHEN** published A1 is remote-reachable and maintainers publish
  `authorize-bounded-terminal-release-authority-activation`
- **THEN** it contains exactly
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-authority-two-stage-boundary.md","investigation_id":"rescue-tiered-release-authority-two-stage-boundary","successor_card":"openspec/board/3.inprogress/implement-terminal-release-authority-activation.md","successor_id":"implement-terminal-release-authority-activation","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** A2 is limited to `<=499` production LOC against the exact published
  A2 authorization HEAD, imports the published A1 contract and cannot redefine
  A1 registry, admission or selector ownership

#### Scenario: A2 exclusively activates terminal release authority
- **WHEN** `implement-terminal-release-authority-activation` runs the canonical
  full-release gate
- **THEN** A2 exclusively owns pre-admission reservation, held `O_EXCL` lock and
  directory fsync, bounded append-only JSONL, atomic terminal publication,
  signal terminalization, strict receipt/marker/manifest equality, required
  review/publish gate, canonical CI activation and its parsed YAML ownership
  oracle
- **AND** no affected result, A1 focused proof, partial JSONL, stale marker,
  mismatched fingerprint or nonterminal process state can authorize review,
  publish or CI success

#### Scenario: A2 receives exactly one atomic terminal capture
- **WHEN** A2 focused checks are GREEN on its unchanged final payload
- **THEN** a fresh Sol/`xhigh` pre-capture audit validates exact lineage,
  `<=499` comparison, A1/A2 ownership, atomicity and connected failure oracles
  before capture ID
  `implement-terminal-release-authority-activation-cycle-1` performs exactly one
  atomic `full-release` capture
- **AND** capture, repair and retry/rescue budget is `0/0/0`; FAIL, timeout,
  signal, malformed or stale receipt, fingerprint change or incomplete terminal
  state is final without a second capture, while the sole unchanged GREEN
  payload proceeds to fresh formal Sol/`xhigh` review

#### Scenario: Downstream acceleration order is immutable
- **WHEN** maintainers continue release-baseline acceleration from this rescue
- **THEN** remote-reachable publication order is A1 authorization, A1
  implementation, A2 authorization, A2 implementation, clean scanner-v2
  authorization and implementation, Windows scheduler authorization and
  implementation, verify-project authorization and implementation, then the
  separate review-preflight and delivery-runner smoke successor
- **AND** no downstream authorization is created before every declared
  predecessor is published, and no successor absorbs another lineage's
  registry, scanner, scheduler, verify-project or smoke ownership

#### Scenario: Rescue fast-forward remains decision-only
- **WHEN** `$changerail-ff` prepares
  `rescue-tiered-release-authority-two-stage-boundary`
- **THEN** it creates or updates only the target card and proposal, design,
  release-CI delta and tasks for one same-slug change
- **AND** production/test/runtime LOC remain zero and no successor card,
  implementation, main-spec sync, history scan, full baseline, archive, review,
  commit or push occurs
