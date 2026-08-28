## ADDED Requirements

### Requirement: Affected v14 investigation MUST terminate v13 and preserve a forensic boundary
Terminal implementation v13 MUST remain unpublished after review cycle 1
reported `9/14`, its sole bounded repair was consumed, and fresh cycle 2
reported `9/14` with descriptor, dangling-symlink, scheduler-matrix and public
rename/copy blockers. Its budget MUST remain exhausted at `1/1/0`.

Only validated verdict summaries and counters MAY cross into v14. The v13 card,
OpenSpec payload, source, tests, CI, synchronized spec mutation, manifest, logs
and raw evidence MUST be forensic-only and MUST NOT be read, copied,
cherry-picked, reproduced or accepted by the clean lineage.

#### Scenario: Exhausted v13 forces investigation before executable v14
- **WHEN** maintainers advance the affected-profile lineage after terminal cycle 2
- **THEN** no further v13 repair or publication is allowed
- **AND** only this clean docs-only investigation may precede authorization v14.

### Requirement: Affected v14 descriptor admission MUST prove exact identity before usability
Future v14 MUST define an independently authored immutable descriptor map that
covers every literal command token, effective-PATH executable, repository input
file, repository input directory and runtime output exactly once. The map MUST
be compared bidirectionally with the production task registry and actual
source/AST command inventory before any probe, Git selection, scheduler call or
filesystem mutation.

Python `>=3.11`, exact runtime/dev package pins and effective real non-symlink
`purelib`/`platlib`, Ruff, Git repository/root identity, Node/npm/npx and
offline OpenSpec `1.3.1` MUST each bind to its exact frozen descriptor. Missing,
extra, duplicate, unknown or ambiguous descriptors; changed literal tokens;
wrong type/access/root; and an alternate but usable executable or target MUST
fail aggregate admission with `semantic_started: 0`. A successful probe of a
wrong OpenSpec command MUST NOT satisfy admission.

#### Scenario: Wrong but usable command fails identity admission
- **WHEN** a fixture substitutes another executable that returns the expected version and exits zero
- **THEN** bidirectional descriptor/source identity fails before the probe can authorize admission
- **AND** Git, scheduler and filesystem mutation remain unstarted.

### Requirement: Affected v14 runtime admission MUST detect dangling symlinks without following
Future v14 MUST inspect the repository root, every runtime-output ancestor,
declared parent and leaf with `lstat` or an equivalent non-following primitive
before any `exists()`-style missing-leaf branch. Every existing directory entry
MUST be classified independently of target resolution.

Existing, dangling or resolving symlink ancestors/leaves, wrong type/access,
lexical or real escape and alternate/non-dedicated roots MUST fail aggregate
admission with zero semantic start and zero mutation. A missing leaf MAY pass
only when no directory entry exists and it is the exact direct child of a real
contained non-symlink writable and searchable parent.

#### Scenario: Broken symlink leaf is existing invalid state
- **WHEN** the exact runtime leaf is a symlink whose target does not exist
- **THEN** non-following admission rejects the leaf rather than treating it as missing
- **AND** no Git command, scheduler reservation or filesystem creation starts.

### Requirement: Affected v14 scheduler proof MUST bind every tuple to source and guard order
Future v14 MUST preserve the complete v11 reason and top-level schema while
defining separate immutable requirement-to-row and requirement-to-mutant maps.
For every valid `completed`, terminal, outer, synthetic and `cancelled` tuple,
each nullable/boolean alternative and numeric lower/interior/upper neighbor
MUST pass through public `profile.main` or `run_smoke`.

Every invalid row case MUST begin from the corresponding passing reason tuple,
change exactly one row field or one top-level invariant, and bind a unique
non-noop actual production-source or AST guard mutant. The observation MUST
prove that every preceding guard passed and that the intended guard was
reached. Completed-only invalid derivation, absent source/AST mutants,
replacement production functions, reused rows, no-op mutations and
earlier-fault masking MUST fail closed.

The top-level map MUST cover exact fields/version/jobs/status, the at/above
64-KiB canonical boundary, result count/identity/order and missing, extra,
duplicate, unknown, reused and cross-ID rows. Required and executable row and
mutant maps MUST compare equal in both directions.

#### Scenario: Data-only completed mutant cannot prove another reason guard
- **WHEN** a catalog claims terminal, outer, synthetic or cancelled coverage from only a completed-row mutation
- **THEN** its canonical-neighbor, source-mutant or guard-order binding is missing
- **AND** bidirectional completeness fails before review or publication.

### Requirement: Affected v14 selector proof MUST close public rename and copy grammar
Future v14 MUST observe committed, staged and unstaged name-status streams and
the untracked NUL path stream through public `profile.main` or `run_smoke`.
For every diff stream the finite catalog MUST include valid A/M/D and valid
R/C scores `000`, an interior score and `100`; R/C MUST consume and select from
both old and new operands.

Each diff stream MUST reject missing old or new operands, every score width,
range, sign, case and status fault, invalid framing or UTF-8 and per-stream byte
overflow. The aggregate catalog MUST also cover path count/length and aggregate
bytes, unknown/self paths and all resolved-base guards. Every uncertainty MUST
select the exact full 35-ID inventory with a bounded reason, zero semantic start
and `authoritative:false`; private-parser-only proof MUST NOT satisfy the gate.

#### Scenario: Valid rename old and new paths both affect public selection
- **WHEN** any diff stream returns a valid NUL-framed `R000..R100` record
- **THEN** the public selector consumes both operands and includes semantics required by each path
- **AND** omitting either operand or changing its score grammar produces full fallback.

### Requirement: Affected v14 investigation MUST freeze one bounded successor order
The only conforming future order MUST be this published investigation,
docs-only `authorize-bounded-affected-release-profile-v14`, clean
`implement-bounded-affected-release-profile-v14`, then
`certify-accelerated-release-loop-v1`.

Future authorization MUST contain exactly:

```json
{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-exhaustive-guard-closure-v14.md","investigation_id":"investigate-affected-release-profile-exhaustive-guard-closure-v14","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v14.md","successor_id":"implement-bounded-affected-release-profile-v14","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It MUST depend exactly on this investigation, the integration decision,
semantic scheduler v1 and authorization v13 and block only implementation v14.
Future implementation MUST use only the exact two-field authorization v14
reference, add at most 499 production LOC, depend on those four predecessors
plus authorization v14 and block only certification.

This investigation MUST add zero production/test/runtime LOC and change only
its card, same-slug OpenSpec artifacts, synchronized release-CI spec and
archive metadata. It MUST NOT create authorization/implementation v14 or
certification and MUST NOT run or accept reachable history, real full/affected
execution or benchmark, live matrix or certification checks. Publication MUST
require one fresh ordinary `gpt-5.6-sol/high` review.

#### Scenario: Investigation remains docs-only and successors remain absent
- **WHEN** maintainers inspect the reviewed investigation payload
- **THEN** production/test/runtime LOC are zero and v14 successor cards and executable surfaces are absent
- **AND** only strict docs/static/current verification has been accepted.
