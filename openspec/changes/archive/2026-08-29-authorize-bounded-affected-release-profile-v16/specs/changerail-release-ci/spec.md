## ADDED Requirements

### Requirement: Affected v16 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v16` as one
docs-only authorization from exact published
`investigate-affected-release-profile-public-proof-closure-v16` commit
`6d31833d7bdaf2605717da6aaaf3519cd6f56eb3`. Before authorization mutation,
the remote investigation and authorization branches MUST both resolve to that
exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, ids, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-public-proof-closure-v16.md","investigation_id":"investigate-affected-release-profile-public-proof-closure-v16","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v16.md","successor_id":"implement-bounded-affected-release-profile-v16","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v16, the accelerated
release-loop integration decision, release semantic scheduler v1 implementation
and affected v15 authorization. It MUST block only
`implement-bounded-affected-release-profile-v16`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v16.md","authorization_id":"authorize-bounded-affected-release-profile-v16"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on investigation v16, the integration decision, scheduler
v1, authorization v15 and this authorization, and block only
`certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v16
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, block and LOC ceiling
- **THEN** only the exact clean implementation v16 successor is eligible
- **AND** any object/path/id/dependency/block/ceiling substitution fails closed.

### Requirement: Affected v16 authorization MUST establish one typed truth before Git
Future v16 MUST define one immutable physical-task registry containing literal
argv, typed operands, immutable origin descriptors, logical IDs and owners.
Literal argv and embedded sequences MUST be extracted independently and compared
bidirectionally with the registry. Parallel ad-hoc truth lists, live-runtime
expected origins and untyped operand aliases MUST fail closed.

Aggregate admission MUST prove repository, origin and package invariants first,
then the exact dedicated runtime root and every selected task root read-only,
and only then permit Git, plan construction and scheduler activation. Python
audit/profile hooks and filesystem snapshots MUST independently observe probe,
process, Git, scheduler and mutation effects without replacing production
functions. Every clean-child fake-first case MUST remain non-authoritative with
`semantic_started:0` before the first later-ledger event.

#### Scenario: Runtime operand or origin fault stops before Git
- **WHEN** any typed operand, origin, package, runtime root or selected task root differs from the single admitted registry
- **THEN** admission returns one bounded non-authoritative result before Git, plan or scheduler
- **AND** independent process, Git, scheduler and mutation ledgers remain empty.

### Requirement: Affected v16 authorization MUST require independent public protocol proofs
Future v16 selector MUST expose public pure framing and ownership boundaries plus
a public real-Git collector that accepts an explicit admitted repository root.
Focused proof MUST create disposable repositories and actually observe
committed, staged, unstaged and untracked streams. Owner-distinct A/M/D and R/C
`000`, interior and `100` tuples, resolved-base guards and every uncertainty row
MUST assert exact registry-ordered public results without monkeypatching
`_run_git` or replacing another production function.

The scheduler summary validator MUST be a public pure trust boundary. A
separately authored immutable requirement map MUST enumerate every valid
reason/top-level tuple and every field, type, bool, integer, bound, cross-field,
size, id, order, count and jobs neighbor. Requirement, executable-case and
semantic-mutant maps MUST have bidirectionally equal IDs and exact node paths
with canonical before/after AST digests; shared expected constants, reused edits,
marker-only changes, no-op mutations and earlier-fault masking MUST fail.

The closed ownership oracle MUST parse canonical runner, profile, scheduler and
broker modules, freeze exact imports, bindings and calls, and enumerate every raw
execution site. Alias, rebind, wrapper, `getattr`, dynamic, duplicate, alternate,
subprocess, `os.system`, `exec` or `eval` sites outside the frozen graph MUST
fail public proof.

#### Scenario: Private, synthetic or incomplete proof cannot authorize affected mode
- **WHEN** selector evidence bypasses real Git, scheduler evidence omits one neighbor, or an execution site escapes the frozen graph
- **THEN** the corresponding public proof fails closed
- **AND** no private helper, shared catalog or marker count can replace the missing observation.

### Requirement: Affected v16 authorization MUST preserve original RED and remain dormant
Before any production, CI or main-spec mutation, future v16 MUST contain only
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

Future v16 MUST preserve independently authored Unicode 16.0.0 `23/235`, exact
35-ID digest and 35-to-30 typed ownership, aggregate admission, typed scheduler
rows and bounded scheduler/summary failures, full-only publication authority,
source-safe four-step CI, connected resolved-base guards and protocol-artifact
non-authority.

Terminal unpublished implementation v15 card, OpenSpec payload, source, tests,
CI, main-spec mutation, manifest, logs and raw evidence MUST remain forensic-only
and MUST NOT be read, copied, cherry-picked, reproduced or accepted. Future v16
MUST be reconstructed only from published contracts after remote publication of
this authorization.

This authorization MUST add zero production, test and runtime LOC and MUST
change only its card, same-slug OpenSpec artifacts, synchronized release-CI spec
and archive metadata. It MUST NOT create implementation v16, focused tests,
production, CI or certification, and MUST NOT run or accept reachable-history,
real full/affected execution, benchmark, live matrix or certification evidence.
One fresh `gpt-5.6-sol/high` ordinary review MUST gate publication.

#### Scenario: Authorization remains docs-only and non-authoritative
- **WHEN** maintainers audit changed paths, successor absence and retained verification
- **THEN** production/test/runtime LOC are zero and executable v16 successor surfaces remain absent
- **AND** affected artifacts have no publication authority and prohibited checks were neither run nor accepted.
