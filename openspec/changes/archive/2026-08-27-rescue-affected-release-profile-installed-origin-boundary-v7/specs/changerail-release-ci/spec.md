## ADDED Requirements

### Requirement: Affected v7 rescue MUST bind a clean successor lineage
The affected v6 implementation MUST remain terminal and unpublished after
review cycle 1 returned `7/12` with three blockers, its sole same-card repair
closed scheduler/authority and connected-proof blockers, and cycle 2 returned
`11/12` with one installed-origin blocker. Its code, card, manifest, verdicts,
logs and evidence MUST remain forensic-only and MUST NOT satisfy future gates.

The only future order MUST be this docs-only investigation/design decision,
docs-only `authorize-bounded-affected-release-profile-v7`, clean
`implement-bounded-affected-release-profile-v7` from the authorization-publishing
HEAD and then `certify-accelerated-release-loop-v1`.

#### Scenario: Exhausted v6 becomes a clean v7 lineage
- **WHEN** cycle 2 proves one installed-origin blocker after the sole repair
- **THEN** v6 cannot receive another same-card patch or publication
- **AND** only the separately authorized clean v7 successor may continue.

### Requirement: Affected v7 MUST admit only exact effective package roots
Future v7 aggregate admission MUST derive installed-distribution roots only
from the effective interpreter's exact `sysconfig.get_paths()` keys `purelib`
and `platlib`. Both values MUST be present, repository-independent, resolvable
and real package directories; the admitted set MUST contain only their resolved
exact paths, deduplicated when equal.

Every exact runtime/dev pinned distribution MUST have an exact version and a
`locate_file("")` origin equal to an admitted package root. `stdlib`,
`platstdlib`, `scripts`, `data`, `include`, a child/prefix match or any arbitrary
existing path MUST NOT qualify. Missing keys, wrong types, symlinks, resolution
errors or uncertainty MUST fail aggregate admission with `semantic_started: 0`
before Git selection, scheduler execution or filesystem mutation.

#### Scenario: Non-package sysconfig roots fail closed
- **WHEN** otherwise exact distribution metadata resolves under any non-package `sysconfig` root
- **THEN** aggregate admission reports the installed-origin fault before semantics
- **AND** no broad mapping iteration or prefix membership can admit it.

### Requirement: Affected v7 MUST connect the production-default origin proof
Future v7 focused proof MUST exercise the production-default package-root
derivation with an exact `purelib`/`platlib` happy neighbor. Independent
otherwise-valid counterexamples MUST cover `stdlib`, `platstdlib`, `scripts`,
`data`, `include`, arbitrary existing origin, wrong per-file pin/version and
wrong effective Python/Ruff executable origin.

Each counterexample MUST weaken or remove the actual production derivation,
exact-equality or executable-binding guard. An explicit injected allowlist,
copied helper, expected-value mutation, source-string assertion or earlier
unrelated failure MUST NOT satisfy the proof.

#### Scenario: Default derivation over-admission is observable
- **WHEN** the production default accepts any non-package root or prefix
- **THEN** its connected named fixture fails after the exact package-root neighbor passes
- **AND** an injected test-only root set cannot mask the counterfactual.

### Requirement: Affected v7 rescue MUST preserve the repaired v6 floor and remain docs-only
Future v7 MUST retain v6's reachable pre-production RED tree and exact 35-ID
digest/35→30 ownership, aggregate pre-mutation admission, strict bounded
four-stream selector, connected resolved-base/runtime/count/byte/order guards,
exact scheduler row types and integer jobs `1|4`, full-only authority, exact
four-step CI and receipt/capture/marker/cache non-authority.

This rescue decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC `0`, create no v7 successor or
certification card, and run or accept no history, real full/affected execution,
benchmark, live matrix or certification evidence.

#### Scenario: Rescue publishes no executable successor
- **WHEN** this installed-origin decision is delivered and reviewed
- **THEN** only docs/OpenSpec scope changes and strict current-only gates run
- **AND** v7 code, tests, CI, runtime authority and certification remain absent.
