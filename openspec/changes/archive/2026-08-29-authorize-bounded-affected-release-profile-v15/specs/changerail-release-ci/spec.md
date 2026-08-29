## ADDED Requirements

### Requirement: Affected v15 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v15` as one
docs-only authorization from exact published
`investigate-affected-release-profile-origin-proof-discrimination-v15` commit
`40208c378cce6c1cea0aef55c8d0abb7cdb34f3e`. Before authorization mutation,
the remote investigation and authorization branches MUST both resolve to that
exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, ids, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-origin-proof-discrimination-v15.md","investigation_id":"investigate-affected-release-profile-origin-proof-discrimination-v15","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v15.md","successor_id":"implement-bounded-affected-release-profile-v15","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v15, the accelerated
release-loop integration decision, release semantic scheduler v1 implementation
and affected v14 authorization. It MUST block only
`implement-bounded-affected-release-profile-v15`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v15.md","authorization_id":"authorize-bounded-affected-release-profile-v15"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on investigation v15, the integration decision, scheduler
v1, authorization v14 and this authorization, and block only
`certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v15
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, block and LOC ceiling
- **THEN** only the exact clean implementation v15 successor is eligible
- **AND** any object/path/id/dependency/block/ceiling substitution fails closed.

### Requirement: Affected v15 authorization MUST preserve independent pre-import origin identity
Future v15 MUST define one immutable typed source-authored origin descriptor for
every executable token. Repository targets MUST derive only from the exact
admitted repository root; Python MUST equal real `sys.executable`; Ruff MUST
derive from the exact effective interpreter scripts root; system and Node tools
MUST derive from closed source-authored per-platform/per-token targets or an
independently validated setup-toolchain anchor. Live `PATH` MUST NOT create,
select, order or freeze expected origin.

The effective `PATH` result MUST equal the one canonical real target and all
launched argv MUST use its admitted absolute path. Zero, alternate, ambiguous,
wrong-token/type/access/root/containment/symlink states MUST aggregate into a
bounded failure with `semantic_started:0` before any version probe, Git command,
scheduler call or filesystem mutation.

The focused pre-import matrix MUST run separate clean-child fake-first-`PATH`
cases for Python, Ruff, Git, Node, npm, npx and the repository OpenSpec target.
A fake returning the exact expected version and exit zero MUST still yield
`authoritative:false` and `semantic_started:0`; fake marker, Git/scheduler
ledgers and runtime-root snapshot MUST remain untouched. Shared descriptor-class
coverage MUST NOT replace any token-specific case.

#### Scenario: Usable fake present before import cannot define expected origin
- **WHEN** a clean child starts with any enumerated fake first in `PATH` before importing the public runner
- **THEN** source-authored identity rejects the fake before probe or mutation
- **AND** an exact-version successful fake cannot upgrade its origin.

### Requirement: Affected v15 authorization MUST preserve discriminating scheduler and selector proof
Future v15 MUST own an immutable normative requirement catalog and a separate
executable case catalog with bidirectionally equal ids. Every origin, scheduler,
selector and ownership data case MUST start from its exact passing neighbor and
run through public `profile.main`, the public runner or `run_smoke` without
replacing production functions or expected constants.

Every claimed distinct mutant MUST change one semantic canonical AST node,
operator or operand and retain exact node path plus before/after digest computed
without test-only markers. Multiple data cases MAY map to one semantic guard
mutant only when each case executes independently and the semantic edit is
counted once. Reused-label edits, marker-only differences, early returns,
no-op mutation, count-only completeness and earlier-fault masking MUST fail.

The scheduler ownership oracle MUST close imports, assignments and calls for
the scheduler module and `run_plan`, permitting exactly one unaliased import and
one direct `ast.Name("run_plan")` call in the single lexical depth-one
activation. Alias import/call, module-qualified call, assignment alias, wrapper,
`getattr`, dynamic dispatch, duplicate/extra call and alternate entrypoint MUST
each be executable semantic source mutants rejected by public proof.

Committed, staged and unstaged A/M/D cases MUST use owner-distinct paths and
assert exact registry-ordered selected-ID tuples. R/C `000`, interior and `100`
cases MUST use different old/new owners and assert both exact owners. Mutants
that drop any status, stream or operand MUST change the public tuple. All base,
process, framing, UTF-8, path/stream/aggregate-bound and unknown/self uncertainty
MUST retain exact 35-ID non-authoritative fallback with zero semantic start.

#### Scenario: Reused mutant or dropped public operand cannot satisfy proof
- **WHEN** a catalog relabels one edit as distinct or source ignores a status, stream or rename/copy operand
- **THEN** mutant identity or exact public tuple proof fails
- **AND** marker counts or membership-only assertions cannot authorize publication.

### Requirement: Affected v15 authorization MUST preserve original RED and remain dormant
Before any production, CI or main-spec mutation, future v15 MUST contain only
its implementation card, same-slug OpenSpec and focused-test artifacts. The
focused test MUST address a genuinely missing production module or symbol and
run directly through `bin/changerail-evidence capture`.

The captured command MUST first print
`bin/changerail-review-verdict fingerprint --workspace .`, then execute the
focused test with a genuine non-zero exit and without `|| true`, an exit-zero
wrapper or substituted failure. One original retained failed entry MUST bind
non-zero `exit_code`, `tree_sha`, `diff_fingerprint` and raw output containing
the specific missing-module/symbol error. The saved tree object MUST exist
before executable mutation and independent review MUST reconstruct it relative
to authorization HEAD to prove no production, CI or main-spec mutation. Later
reproduction MUST NOT satisfy chronology.

Future v15 MUST preserve the published Unicode 16.0.0 `23/235` oracle, exact
35-ID digest and 35-to-30 typed ownership, aggregate descriptor/package/runtime/
task-root admission, typed scheduler rows, bounded scheduler/summary failures,
full-only publication authority, source-safe four-step CI, connected
resolved-base guards and protocol-artifact non-authority.

Terminal unpublished implementation v14 card, OpenSpec payload, source, tests,
CI, main-spec mutation, manifest, logs and raw evidence MUST remain forensic-only
and MUST NOT be read, copied, cherry-picked, reproduced or accepted. Future v15
MUST be reconstructed only from published contracts after remote publication of
this authorization.

This authorization MUST add zero production, test and runtime LOC and MUST
change only its card, same-slug OpenSpec artifacts, synchronized release-CI spec
and archive metadata. It MUST NOT create implementation v15, focused tests,
production, CI or certification, and MUST NOT run or accept reachable-history,
real full/affected execution, benchmark, live matrix or certification evidence.
One fresh `gpt-5.6-sol/high` ordinary review MUST gate publication.

#### Scenario: Authorization remains docs-only and non-authoritative
- **WHEN** maintainers audit changed paths, successor absence and retained verification
- **THEN** production/test/runtime LOC are zero and executable v15 successor surfaces remain absent
- **AND** affected artifacts have no publication authority and prohibited checks were neither run nor accepted.
