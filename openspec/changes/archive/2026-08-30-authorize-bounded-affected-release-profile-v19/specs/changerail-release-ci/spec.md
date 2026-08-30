## ADDED Requirements

### Requirement: Affected v19 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v19` as one
docs-only authorization from exact published
`investigate-affected-release-profile-hosted-origin-activation-closure-v19`
commit `8d513a9564012b10225c0012ceff32573cef7706`. Before authorization
mutation, the local/upstream/remote authorization branch and remote
investigation branch MUST resolve to that exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, IDs, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-hosted-origin-activation-closure-v19.md","investigation_id":"investigate-affected-release-profile-hosted-origin-activation-closure-v19","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v19.md","successor_id":"implement-bounded-affected-release-profile-v19","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v19, the accelerated
release-loop integration decision, release semantic scheduler v1
implementation and authorization v18. It MUST block only
`implement-bounded-affected-release-profile-v19`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v19.md","authorization_id":"authorize-bounded-affected-release-profile-v19"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on those four predecessors plus this authorization and
block only `certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v19
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, sole block, base and LOC ceiling
- **THEN** only the exact clean implementation v19 successor is eligible
- **AND** any object, path, ID, dependency, block, ceiling or base substitution fails closed.

### Requirement: Affected v19 authorization MUST preserve the immutable v18 proof anchor
Future v19 MUST use unchanged published
`openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
as its sole external command/typed-operand anchor. It MUST preserve exact
section counts `35/30/48`, semantic SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
canonical full SHA-256
`6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
total 35→30 ownership and exact `36 - 4 - (3 - 1) = 30` migration.

V19 MUST NOT copy, regenerate, supersede or modify that inventory. Future
production registry/extraction and independently implemented proof parser MUST
compare bidirectionally with the already-published rows/digests. The inventory
MUST remain proof-only with no runtime, wire, receipt or publication authority.

#### Scenario: V19 cannot move the published command anchor
- **WHEN** a future command, operand, origin, target, owner, map, count or digest differs from authorization v18 inventory
- **THEN** v19 proof fails even if production metadata and parser drift together
- **AND** neither execution success nor a copied v19 inventory can replace the immutable anchor.

### Requirement: Affected v19 authorization MUST require actual hosted-origin observation
Future v19 focused proof MUST run separate clean-child cases for `node`, `npm`
and `npx`. An independent oracle MUST parse the exact pinned four-step CI and
derive each canonical setup-node Linux target from an externally constructed
real absolute `RUNNER_TOOL_CACHE`, exact `node/<20.x.y>/<arch>/bin` grammar and
bounded npm/npx launcher resolution without importing production descriptors,
expected sets, branch markers or results.

Each valid case MUST place an exact-version successful fake for its token first
in PATH and externally observe the exact selected toolcache target/argv while
the fake remains unused. Local `_SYSTEM_ORIGINS`, live-PATH selection,
successful usability, or production-declared hosted markers MUST NOT satisfy a
hosted case.

Absent/relative/symlinked/outside root, wrong or duplicate version/
architecture/token, zero or multiple target, unsafe launcher, fake-first
selection or hosted-to-system fallback MUST fail before semantics. External
profile/audit/process hooks and snapshots MUST prove bounded non-authoritative
`semantic_started:0` output and zero later Git, scheduler, write-intent and
mutation events.

#### Scenario: Every hosted token has an independent branch witness
- **WHEN** future focused proof claims hosted origin admission
- **THEN** `node`, `npm` and `npx` each select the independently derived setup-node toolcache target in a separate fake-first clean child
- **AND** local-origin coverage, branch labels or three shared-class assertions cannot substitute any token witness.

### Requirement: Affected v19 authorization MUST require observed activation equality and dynamic reachability
Future v19 MUST independently parse exact affected runner/profile and
exact-digest scheduler/broker source, inventory every import, binding,
function, predicate, call and raw sink and run a finite context-sensitive
worklist from the exact public affected entrypoint/production argument row with
`supervisor=None`.

Every observed row MUST include stable identity/kind, repository-relative
source and digest, qualified owner and canonical AST path, normalized context/
predicate facts, exact finite callee/receiver set, reachability and exact latent
reason or sink classification. The complete observed row multiset MUST compare
bidirectionally on every field with separately authored immutable
`ACTIVATION_CATALOG`. Counts/uniqueness, self-derived rows, extra/missing rows,
unknown/empty/ambiguous binding, runtime rebind or latent transition MUST fail.

A separate clean child with pre-import profile/audit hooks MUST invoke exact
public affected activation and make its dynamic reachable call/sink projection
equal the static reachable projection through scheduler default and broker.
The injected non-None supervisor path MUST remain observed/cataloged with an
exact predicate-backed unreachable reason. Trace absence MUST NOT prove a
latent row; every reachable row requires its dynamic witness.

#### Scenario: Catalog structure alone cannot authorize activation
- **WHEN** catalog identities/counts pass but observed rows, exact field equality, reachable trace witness or latent reason is missing
- **THEN** activation proof fails before affected evidence is admitted
- **AND** alternate wrapper/sink, non-None supervisor or self-derived observation cannot gain authority.

### Requirement: Affected v19 authorization MUST preserve original RED and remain dormant
Before production, CI or main-spec mutation, future implementation MUST contain
only its card, same-slug OpenSpec and focused-test artifacts and retain a direct
fingerprint-first `bin/changerail-evidence capture` failure with non-zero exit,
reachable saved tree and concrete missing production module or symbol. Later
reproduction, zero-exit wrapper and terminal-v18 evidence MUST NOT satisfy
chronology.

Future v19 MUST preserve exact 35→30 semantics, independently authored Unicode
16.0.0 `23/235`, aggregate repository/origin/package/runtime/task-root
admission before Git, strict public pure and honest real-Git four-stream
selection, typed scheduler and bounded failures, connected guard mutants,
full-only publication authority, protocol-artifact non-authority, closed
runner/profile/scheduler/broker ownership and exact source-safe four-step CI.

This authorization MUST change only its card, same-slug OpenSpec artifacts,
synchronized release-CI spec and archive metadata. It MUST add production/test/
runtime LOC `0`, create no implementation or certification artifact and MUST
NOT run or accept reachable history, real full/affected execution, benchmark,
live matrix or certification evidence. One fresh ordinary
`gpt-5.6-sol/high` review MUST gate publication.

#### Scenario: Authorization cannot execute or certify affected work
- **WHEN** maintainers audit changed paths, successor absence, LOC and verification
- **THEN** only exact lineage and future proof constraints change with zero executable LOC
- **AND** affected/proof artifacts remain non-authoritative while implementation and certification stay absent.
