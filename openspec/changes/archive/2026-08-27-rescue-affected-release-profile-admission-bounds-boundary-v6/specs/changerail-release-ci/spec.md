## ADDED Requirements

### Requirement: Admission/bounds investigation MUST replace terminal unpublished affected v5
ChangeRail MUST publish
`rescue-affected-release-profile-admission-bounds-boundary-v6` as one docs-only
investigation/design decision from exact published
`authorize-bounded-affected-release-profile-v5` tip
`3588c1d3de0ddc9d8ef50e81992620fc107e4e90`.

The unpublished `implement-bounded-affected-release-profile-v5` lineage MUST be
terminal, non-conforming and forensic-only after review cycle 1 `NO-GO` at
`10/12`, one consumed same-card repair and review cycle 2 `NO-GO` at `9/12`.
Its code, card, manifest, verdicts, logs and evidence MUST NOT be read, copied,
cherry-picked or accepted by a future dependency, authorization,
implementation, verification, review or publication gate. Only the concise
reviewed finding classes MAY inform this decision.

The only conforming future order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v6`, clean
`implement-bounded-affected-release-profile-v6`, then
`certify-accelerated-release-loop-v1`. The v6 authorization MUST contain exactly
one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md","investigation_id":"rescue-affected-release-profile-admission-bounds-boundary-v6","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v6.md","successor_id":"implement-bounded-affected-release-profile-v6","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-admission-bounds-boundary-v6`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v5`. It MUST block only
`implement-bounded-affected-release-profile-v6`.

The v6 implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v6.md","authorization_id":"authorize-bounded-affected-release-profile-v6"}
```

It MUST depend exactly on those four predecessors plus authorization v6, block
only certification, start from the authorization-publishing HEAD, add at most
499 production LOC and reconstruct only from published sources.

#### Scenario: Investigation leaves one clean v6 path
- **WHEN** maintainers publish this decision from exact safe tip `3588c1d3...`
- **THEN** terminal v5 remains forensic-only and exact v6 lineage becomes exclusive
- **AND** authorization v6, implementation v6 and certification remain absent.

### Requirement: Affected v6 MUST admit runtime output before filesystem mutation
Future v6 MUST complete aggregate toolchain and target admission before Git
selection, semantic scheduling and any runtime-output `mkdir`, `mkdtemp`, file
creation or state mutation. The runtime-output descriptor MUST be bounded to an
exact repository-local path and MUST validate both the leaf and its nearest
existing parent.

An absent leaf MAY pass only beneath a real non-symlink repository-local
writable/searchable directory. An existing leaf MAY pass only when it is a real
non-symlink writable/searchable directory. Existing regular file, symlink,
other wrong type, root escape, missing/inaccessible/uncertain parent or access
failure MUST produce a bounded aggregate admission failure with
`semantic_started: 0`. The CLI entrypoint MUST emit the bounded report and MUST
NOT raise an exception before that report.

#### Scenario: Runtime-output existing file fails before mutation
- **WHEN** the exact runtime-output target exists as a regular file before v6 starts
- **THEN** aggregate admission reports the target fault with `semantic_started: 0`
- **AND** no runtime directory, selector command or scheduler task starts and the entrypoint does not escape with an uncaught exception.

#### Scenario: Runtime-output parent and leaf types are closed
- **WHEN** the leaf is absent under a valid parent or exists as a valid directory
- **THEN** target admission may proceed without creating publication authority
- **AND** symlink, escape, wrong-type or inaccessible parent/leaf variants fail closed before mutation.

### Requirement: Affected v6 MUST connect every selector bound to a named counterfactual
Future v6 focused proof MUST independently reach and validate per-path
`MAX_PATH`, aggregate/deduplicated `MAX_PATHS`, per-stream `MAX_GIT_BYTES` for
committed, staged, unstaged and untracked streams, and aggregate four-stream
`MAX_GIT_BYTES`. Each fault fixture MUST have otherwise valid Git/base/framing
inputs and MUST identify the exact bound it crosses.

For every bound, a finite non-noop counterfactual MUST remove or weaken only
the actual production guard reached by the named fixture. The focused gate MUST
fail when that guard is absent. A source-string assertion, earlier failure,
wrong helper, expected-value mutation, digest shield or copied result MUST NOT
count. Runtime-output existing-file/type/order faults MUST receive the same
connected admission and guard-mutant treatment.

#### Scenario: Each path/count/byte guard removal is observable
- **WHEN** a named per-path, path-count, per-stream-byte or aggregate-byte guard is removed or weakened
- **THEN** its otherwise-valid connected fixture fails
- **AND** no other earlier guard or fallback can satisfy that counterfactual.

#### Scenario: Runtime-output guard and ordering mutants are observable
- **WHEN** a counterfactual accepts an existing file or creates runtime state before target admission
- **THEN** the focused target fixture fails and records that semantics remained unstarted
- **AND** a caught unrelated exception or test-only result mutation cannot satisfy proof.

### Requirement: Admission/bounds investigation MUST preserve v5 floor and remain docs-only
Future v6 MUST retain real pre-production RED chronology and the published v5
floor: exact 35-ID digest and 35→30 ownership, aggregate admission, strict
four-stream NUL/status grammar, typed scheduler rows/jobs, full-only authority,
exact source-safe four-step CI, connected resolved-base guards and
protocol-artifact non-authority.

This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create v6 successor cards,
code, tests, dependencies, schemas, CI or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
execution/benchmark, live matrix, certification or terminal prototype evidence.
It requires one fresh Sol/high review and permits one same-card docs repair.

#### Scenario: Investigation cannot claim executable closure
- **WHEN** this decision is planned, delivered, reviewed or published
- **THEN** only exact lineage and future admission/proof requirements change
- **AND** executable closure and certification remain absent.
