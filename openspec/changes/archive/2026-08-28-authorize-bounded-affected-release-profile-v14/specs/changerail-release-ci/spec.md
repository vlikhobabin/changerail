## ADDED Requirements

### Requirement: Affected v14 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v14` as one
docs-only authorization from exact published
`investigate-affected-release-profile-exhaustive-guard-closure-v14` commit
`c884971ccca3d4d6ab4d76f27c22122981131d16`. Before authorization mutation,
the remote investigation and authorization branches MUST both resolve to that
exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, ids, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-exhaustive-guard-closure-v14.md","investigation_id":"investigate-affected-release-profile-exhaustive-guard-closure-v14","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v14.md","successor_id":"implement-bounded-affected-release-profile-v14","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v14, the accelerated
release-loop integration decision, release semantic scheduler v1 implementation
and affected v13 authorization. It MUST block only
`implement-bounded-affected-release-profile-v14`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v14.md","authorization_id":"authorize-bounded-affected-release-profile-v14"}`,
start from the authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on investigation v14, the integration decision, scheduler
v1, authorization v13 and this authorization, and block only
`certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v14
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, block and LOC ceiling
- **THEN** only the exact clean implementation v14 successor is eligible
- **AND** any object/path/id/dependency/block/ceiling substitution fails closed.

### Requirement: Affected v14 authorization MUST preserve descriptor and non-following runtime admission
Future v14 MUST define an independently authored immutable descriptor map that
covers every literal command token, effective-PATH executable, repository input
file, repository input directory and runtime output exactly once. Before any
probe, Git selection, scheduler call or filesystem mutation, the map MUST be
compared bidirectionally with the production task registry and actual
source/AST command inventory.

Python `>=3.11`, exact runtime/dev pins, effective real non-symlink
`purelib`/`platlib`, Ruff, Git repository/root identity, Node/npm/npx and
offline OpenSpec `1.3.1` MUST each bind to its exact frozen descriptor. Missing,
extra, duplicate, unknown, ambiguous or changed descriptors, wrong types,
access or roots and alternate-but-usable executables/targets MUST fail aggregate
admission before Git, scheduler and mutation with `semantic_started: 0`.

The repository root, every runtime-output ancestor, parent and leaf MUST be
inspected with `lstat` or an equivalent non-following primitive before any
`exists()`-style missing-leaf branch. Existing, dangling or resolving symlink
entries, wrong type/access, lexical or real escape and alternate/non-dedicated
roots MUST fail with zero semantic start and zero mutation. A missing leaf MAY
pass only when no directory entry exists and it is the exact direct child of a
real contained non-symlink writable and searchable parent.

#### Scenario: Wrong usable command or dangling leaf fails before semantics
- **WHEN** a fixture supplies a usable alternate command or a symlink leaf whose target is missing
- **THEN** exact descriptor or non-following path admission rejects it before any Git command, scheduler reservation or filesystem creation
- **AND** target usability or `exists() == false` cannot satisfy admission.

### Requirement: Affected v14 authorization MUST preserve source-bound scheduler and public selector closure
Future v14 MUST preserve the complete v11 reason and top-level schemas while
owning separate immutable requirement-to-row and requirement-to-mutant maps.
Every valid completed, terminal, outer, synthetic and cancelled tuple,
nullable/boolean alternative and numeric lower/interior/upper neighbor MUST
pass through public `profile.main` or `run_smoke`.

Every invalid row case MUST start from its corresponding passing reason tuple,
change exactly one row field or top-level invariant and bind one unique non-noop
actual production-source or AST guard mutant. Proof MUST show every preceding
guard passed and the intended guard was reached. Completed-only derivation,
missing source mutants, replacement functions, reused/no-op rows and
earlier-fault masking MUST fail bidirectional completeness.

The top-level catalog MUST cover exact fields/version/jobs/status, the exact
64-KiB boundary, result count/identity/order and missing, extra, duplicate,
unknown, reused and cross-ID rows, including boolean-as-int, wrong JSON types
and cross-field values.

Public selection MUST observe committed, staged and unstaged name-status
streams and the untracked NUL path stream. Every diff stream MUST cover valid
A/M/D and R/C scores `000`, an interior score and `100`, consuming both old and
new operands, and reject missing operands, every score width/range/sign/case/
status fault, framing/UTF-8 faults and per-stream overflow. Aggregate path
count/length/bytes, unknown/self paths and resolved-base guards MUST also be
closed. Every uncertainty MUST select the exact full 35-ID inventory with a
bounded reason, `semantic_started: 0` and `authoritative:false`.

#### Scenario: Disconnected mutant or incomplete rename proof fails closed
- **WHEN** a catalog uses a completed-derived/private-parser-only case, masks an earlier guard or omits either valid rename/copy operand
- **THEN** source/guard or public stream completeness fails before review or publication
- **AND** uncertainty becomes exact 35-ID non-authoritative fallback without semantic start.

### Requirement: Affected v14 authorization MUST preserve original chronology and the accumulated floor while remaining dormant
Before any production, CI or main-spec mutation, future v14 MUST contain only
its implementation card, same-slug OpenSpec and focused-test artifacts. The
focused test MUST import the genuinely absent production module
`changerail_release_affected_profile` and run directly through
`bin/changerail-evidence capture`.

The captured command MUST first print
`bin/changerail-review-verdict fingerprint --workspace .`, then execute the
focused test with a genuine non-zero exit and without `|| true`, exit-zero
wrapper or substituted failure. One original retained entry MUST bind
`status: failed`, non-zero `exit_code`, `tree_sha`, `diff_fingerprint` and a raw
output line exactly equal to
`ModuleNotFoundError: No module named 'changerail_release_affected_profile'`.
The saved tree object MUST exist before executable mutation and independent
review MUST reconstruct it relative to exact authorization HEAD to prove no
production, CI or main-spec mutation. Fragments, reconstruction and later
reproduction MUST NOT satisfy chronology.

Future v14 MUST preserve the independent Unicode 16.0.0 `Cc|Cf` oracle with
exactly 23 ordered non-overlapping ranges, 235 scalar values, U+11F00
nonmembership and digest
`7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81`.
The test-only literal set MUST be separately authored from frozen category data
and MUST independently derive boundaries and the digest preimage of ascending
six-uppercase-hex-digit `START-END` records joined by ASCII `;` without
whitespace, BOM, newline or trailing delimiter.

Future v14 MUST preserve exactly one lexical depth-one direct call from
`profile.main` to unaliased imported `run_plan` plus connected public
runner/profile/scheduler observation, the v11 dedicated runtime-root and
read-only task-root reservation floor, exact 35-ID digest and 35-to-30 typed
ownership, aggregate pre-mutation admission, effective `purelib`/`platlib`
origins, strict committed/staged/unstaged/untracked NUL selection,
scheduler-v1 sole activation, full-only publication authority, exact
source-safe four-step CI, connected resolved-base guards and protocol-artifact
non-authority.

Terminal unpublished v13 card, OpenSpec payload, source, tests, CI, main-spec
mutation, manifest, logs and raw evidence MUST remain forensic-only and MUST
NOT be read, copied, cherry-picked, reproduced or accepted. Future v14 MUST be
reconstructed only from published contracts after remote publication of this
authorization.

This authorization MUST add zero production, test and runtime LOC and MUST
change only its card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` spec and archive metadata. It MUST NOT create the v14
implementation card, focused tests, production, CI or certification, and MUST
NOT run or accept reachable-history scan, real full baseline, affected
execution/benchmark, live matrix or certification evidence. One fresh
`gpt-5.6-sol/high` ordinary review MUST gate publication.

#### Scenario: Authorization remains docs-only and non-authoritative
- **WHEN** maintainers audit changed paths, successor absence and retained verification
- **THEN** production/test/runtime LOC are zero and executable v14 successor surfaces remain absent
- **AND** affected execution/artifacts have no publication authority and prohibited checks were neither run nor accepted.
