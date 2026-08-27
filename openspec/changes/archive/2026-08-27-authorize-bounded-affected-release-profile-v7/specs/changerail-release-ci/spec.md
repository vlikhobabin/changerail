## ADDED Requirements

### Requirement: Affected v7 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v7` as one
docs-only authorization from exact published
`rescue-affected-release-profile-installed-origin-boundary-v7` commit
`932b3c5643b009e5a2f372c4c6b4ca803cac1d87`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-installed-origin-boundary-v7.md","investigation_id":"rescue-affected-release-profile-installed-origin-boundary-v7","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v7.md","successor_id":"implement-bounded-affected-release-profile-v7","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-installed-origin-boundary-v7`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v6`. It MUST block only
`implement-bounded-affected-release-profile-v7`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v7.md","authorization_id":"authorize-bounded-affected-release-profile-v7"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the four published predecessors above plus this
authorization and block only `certify-accelerated-release-loop-v1`. Its card,
change, focused tests and executable payload MUST remain absent until this
authorization is committed, reviewed, pushed and remotely reachable.

#### Scenario: Authorization leaves one bounded successor absent
- **WHEN** maintainers deliver or review this authorization
- **THEN** exact source object, dependencies, sole block and future reference are machine-checkable
- **AND** the v7 implementation successor remains absent until publication.

### Requirement: Affected v7 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v7 MUST contain only its
card, same-slug OpenSpec and focused-test artifacts and MUST run its real failing
focused test through `bin/changerail-evidence capture`. The captured command
MUST first emit `bin/changerail-review-verdict fingerprint --workspace .` and
then run the test while preserving the test's non-zero exit status.

The retained entry MUST have `status: failed`, a non-zero `exit_code` and raw
output containing the pre-production `tree_sha`, `diff_fingerprint` and a
concrete absent production symbol/module error. The captured tree object MUST
remain reachable before production mutation. A zero-exit wrapper, synthetic
note, unsaved run or later reproduction MUST NOT satisfy chronology.

The independent reviewer MUST reconstruct the retained tree relative to exact
authorization HEAD and prove that production, CI and main-spec paths were
unchanged. Missing object reachability, forbidden paths, non-specific failure
or post-production capture MUST fail closed.

#### Scenario: Authorization rejects unauditable RED chronology
- **WHEN** v7 requests review without a retained failing pre-production tree and specific missing-symbol/module error
- **THEN** the RED acceptance criterion fails
- **AND** later reproduction or a successful wrapper cannot repair that lineage.

### Requirement: Affected v7 authorization MUST admit only exact effective package roots
Future v7 aggregate admission MUST derive installed-distribution roots only
from the effective interpreter's exact `sysconfig.get_paths()` keys `purelib`
and `platlib`. Both values MUST be present, resolvable, real non-symlink package
directories; the admitted set MUST contain only their resolved exact paths and
MAY deduplicate them only when equal.

Every exact runtime/dev pinned distribution MUST have its exact version and a
`locate_file("")` origin equal to one admitted package root. `stdlib`,
`platstdlib`, `scripts`, `data`, `include`, child/prefix matches or arbitrary
existing paths MUST NOT qualify. Missing keys, wrong types, symlinks,
resolution errors or uncertainty MUST fail aggregate admission with
`semantic_started: 0` before Git selection, scheduler execution or filesystem
mutation.

Ruff `0.6.9` MUST bind its exact framed version, installed-distribution origin
and executable origin in the selected interpreter's bin directory. Pinned
OpenSpec `1.3.1` MUST remain exact and offline.

#### Scenario: Non-package sysconfig roots fail before semantics
- **WHEN** otherwise exact distribution metadata resolves under any non-package sysconfig root or prefix
- **THEN** aggregate admission reports the installed-origin fault with `semantic_started: 0`
- **AND** no selector, scheduler task or runtime-output mutation starts.

### Requirement: Affected v7 authorization MUST require production-default connected origin proof
Future v7 focused proof MUST exercise the actual production-default package-root
derivation with an exact `purelib`/`platlib` happy neighbor. Independent
otherwise-valid counterexamples MUST cover `stdlib`, `platstdlib`, `scripts`,
`data`, `include`, arbitrary existing origin, wrong per-file pin/version and
wrong effective Python/Ruff executable origin.

Each case MUST weaken or remove the actual production derivation,
exact-equality or executable-binding guard. An explicit injected allowlist,
copied helper, expected-value mutation, source-string assertion, earlier
unrelated failure or protocol artifact MUST NOT satisfy the proof.

Future v7 MUST retain connected non-noop production-guard mutants for
resolved-base faults, runtime-output ordering/type faults, per-path `MAX_PATH`,
aggregate/deduplicated `MAX_PATHS`, every committed/staged/unstaged/untracked
stream's `MAX_GIT_BYTES` and aggregate four-stream `MAX_GIT_BYTES`. Every fault
fixture MUST otherwise have valid Git/base/framing/admission input and reach its
named production guard.

#### Scenario: Default derivation over-admission is observable
- **WHEN** the production default accepts any non-package root or prefix
- **THEN** its connected named fixture fails after the exact package-root neighbor passes
- **AND** injected roots or a different earlier guard cannot mask the defect.

### Requirement: Affected v7 authorization MUST preserve the repaired floor and remain dormant
Future v7 MUST retain reachable pre-production RED, exact 35-ID digest and
35→30 ownership, aggregate pre-mutation admission, strict bounded four-stream
Git parsing, connected selector/runtime guards, typed scheduler rows and exact
integer jobs `1|4`, full-only authority, exact source-safe four-step CI and
receipt/capture/marker/cache non-authority from published sources.

This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

Terminal unpublished v6 code, card, manifest, verdicts, logs and evidence MUST
NOT be read, copied, cherry-picked or accepted. This authorization MUST NOT run
or accept reachable history, real full baseline, affected execution/benchmark,
live matrix or certification evidence. It requires one fresh Sol/high review
and permits one same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization
- **THEN** only exact lineage and future verification constraints change
- **AND** selector, scheduler, history, full, affected, live and certification work remains absent.
