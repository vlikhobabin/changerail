## ADDED Requirements

### Requirement: Affected v11 investigation MUST replace terminal unpublished v10
ChangeRail MUST publish
`investigate-affected-release-profile-runtime-root-scheduler-matrix-v11`
docs-only from exact safe affected v10 authorization commit
`fb43b46fdc4a746eabdc8325c231f4724daccb44`. Terminal unpublished v10 ended
after review cycle 1, one bounded repair and fresh cycle-2 `NO-GO` with `7/9`
acceptance, two blockers and rescue budget `1/1/0` exhausted. Its card, source,
tests, specs, manifest, verdicts, logs and raw evidence MUST remain
forensic-only; only these concise validated outcomes MAY cross this clean
lineage boundary.

Terminal v10 MUST NOT be repaired or published. Before a separately reviewed
and remotely published authorization v11, no v11 implementation card, focused
test, production, CI or main-spec executable mutation MAY exist.

#### Scenario: Exhausted v10 forces a docs-only investigation
- **WHEN** v10 retains two blockers after its sole repair and fresh cycle-2 review
- **THEN** another v10 patch or executable v11 payload is forbidden
- **AND** only this clean docs-only investigation may advance the lineage.

### Requirement: Affected v11 runtime-root admission MUST require one exact dedicated target
Future v11 MUST admit the scheduler runtime root as the exact frozen
repository-relative runtime-output descriptor before Git selection,
`run_plan` or filesystem mutation. The leaf MUST be one non-empty ASCII token
of at most 128 encoded bytes, begin with an alphanumeric character, contain
only alphanumeric characters plus `._-`, and MUST NOT equal `.` or `..`.

Admission MUST reject empty, NUL-containing, surrogate or otherwise
non-encodable, overlong, absolute, multi-component or alternate leaf values;
the repository root itself; lexical or resolved escape; symlinked ancestor or
leaf; wrong type or insufficient read/search/write access; and every
non-dedicated target. Every existing ancestor, parent and leaf MUST resolve as
a real non-symlink directory beneath the real repository root. A missing leaf
MAY pass only when it is the exact direct child of its real non-symlink,
contained, writable and searchable declared parent.

Any fault MUST contribute to one bounded aggregate admission failure with
`semantic_started: 0` before Git, scheduler, `mkdir`, `mkdtemp`, file creation
or other state mutation. The public CLI MUST emit the bounded report and MUST
NOT escape with an uncaught path encoding, resolution or access exception.

#### Scenario: Contained but non-dedicated runtime root fails closed
- **WHEN** runtime-root input is empty, `.`, the repository root, an alternate
  contained path, malformed leaf, symlink, wrong type, inaccessible or escaped
- **THEN** aggregate admission records the exact bounded fault with `semantic_started: 0`
- **AND** no Git command, scheduler call or filesystem mutation starts.

#### Scenario: Exact missing dedicated leaf passes read-only admission
- **WHEN** the frozen leaf is absent as a direct child of its real contained
  non-symlink writable and searchable declared parent
- **THEN** runtime-root admission may succeed without creating the leaf
- **AND** scheduler reservation remains the only later filesystem owner.

### Requirement: Affected v11 MUST prove every selected task root before reservation
Future v11 MUST perform a read-only pre-reservation proof for every selected
scheduler task root before calling `run_plan`. Every root MUST use the exact
bounded direct-child token grammar, be unique, remain lexically and really
contained beneath the admitted runtime root, and have no existing leaf,
symlink or filesystem conflict.

All selected roots MUST be evaluated in one aggregate admission pass. Any
missing, duplicate, malformed, escaped, existing, symlinked or conflicting
row MUST produce one bounded aggregate failure with `semantic_started: 0` and
zero filesystem mutation. A race after admission or an atomic reservation
failure MUST remain a bounded scheduler failure, MUST grant no authority and
MUST clean up only roots created by that reservation attempt.

#### Scenario: One conflicting task root blocks the complete plan before mutation
- **WHEN** one selected root is existing, symlinked, duplicated, malformed or escaped
- **THEN** aggregate admission reports the task-root fault before `run_plan`
- **AND** no task root is reserved and no semantic task starts.

#### Scenario: Reservation race remains bounded and non-authoritative
- **WHEN** every read-only proof passes but a root conflicts during atomic reservation
- **THEN** the scheduler fails closed and removes only roots it created
- **AND** the result cannot authorize review, publish, receipt or certification.

### Requirement: Affected v11 scheduler proof MUST use an independently complete matrix
Future v11 MUST define a normative requirement-to-row map independently of its
executable mutant catalog and a separate immutable reason schema containing
exactly `completed`; terminal `child_failed`, `execution_timeout`,
`output_limit`, `cleanup_incomplete`, `internal_error`; outer
`protocol_error`, `broker_lost`, `outer_timeout`, `outer_cleanup_error`;
synthetic `supervisor_result_error`, `supervisor_error`, `executor_error`; and
`cancelled`.

The reason schema MUST preserve every published valid tuple: `completed` is
pass/`0`/output `0..8192`/cleanup true/messages `3`; `child_failed` is
fail/nonzero integer/`0..8192`/true/`3`; `execution_timeout` is fail/integer/
`0..8192`/true/`3`; `output_limit` is fail/integer/`8193`/true/`3`;
`cleanup_incomplete` is fail/null-or-integer/`0..8193`/false/`3`;
`internal_error` is fail/null-or-integer/`0..8192`/boolean/`3`; every outer
reason is fail/null-or-integer/`0`/false/messages `0..2`; every synthetic
reason is fail/null/`0`/false/`0`; and `cancelled` is fail/null/`0`/true/`0`.
Reason text MUST be a non-empty ASCII token of at most 64 encoded bytes.

For every reason, the map MUST name canonical neighbors for every allowed
nullable/boolean alternative and each numeric lower, interior and upper
boundary. It MUST independently require one-field invalid cases for exact row
field set, `id`, `status`, `reason`, `returncode`, `output_bytes`,
`cleanup_complete` and `messages`, including wrong JSON type and boolean-as-int,
missing/extra, unknown/empty, below/above bound and cross-field values valid
only for a different reason.

Top-level rows MUST cover exact fields `version`, `status`, `jobs`, `results`;
exact scheduler-v1 version; jobs of exact integer type equal to requested `1`
or `4`; all-pass versus any-fail status; canonical JSON size at and above 64
KiB; exact result count, planned identity and registry order; and missing,
extra, duplicate, unknown, reused and cross-ID rows.

The executable catalog and independent required-row set MUST be equal in both
directions. Every row MUST bind a unique non-noop actual production-source or
AST mutant, a valid canonical neighbor, public `profile.main` or `run_smoke`
observation and proof that preceding guards passed without replacement
production functions. Missing, extra, duplicate or reused rows, masked faults,
untested valid tuples, accepted one-field mutants and private-helper-only proof
MUST fail closed.

#### Scenario: A self-consistent incomplete catalog cannot prove completeness
- **WHEN** the executable catalog omits a required reason, boundary or cross-field row
- **THEN** bidirectional comparison with the independent requirement map fails
- **AND** a catalog-local count or digest cannot mask the omission.

#### Scenario: Every valid neighbor and one-field mutant reaches the public boundary
- **WHEN** focused verification enumerates the immutable reason schema and top-level matrix
- **THEN** every canonical neighbor passes and every one-field mutant fails through `profile.main` or `run_smoke`
- **AND** reused, no-op, disconnected or earlier-fault-masked mutants are rejected.

### Requirement: Affected v11 investigation MUST preserve the floor and freeze one future order
The only conforming future order MUST be this published investigation,
docs-only `authorize-bounded-affected-release-profile-v11`, clean
`implement-bounded-affected-release-profile-v11`, then
`certify-accelerated-release-loop-v1`. Future authorization MUST bind only the
exact implementation successor and a production ceiling no greater than 500;
future implementation MUST add no more than 499 production LOC and reconstruct
only from published sources.

Future v11 MUST preserve the exact 35-ID digest and 35→30 typed ownership,
aggregate pre-mutation admission, effective `purelib`/`platlib` origins, strict
committed/staged/unstaged/untracked NUL selector, scheduler-v1 sole activation,
full-only authority, exact source-safe four-step CI, connected resolved-base
guards and protocol-artifact non-authority.

This investigation MUST add production, test and runtime LOC `0` and modify
only its card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` specification and archive metadata. Authorization and
implementation v11 and certification MUST remain absent. Reachable history,
real full baseline, affected execution or benchmark, live matrix and
certification checks MUST NOT run or be accepted.

#### Scenario: Investigation changes only the future proof contract
- **WHEN** maintainers plan, deliver, review or publish this investigation
- **THEN** exact runtime-root, scheduler-matrix, lineage and ceiling constraints become durable
- **AND** executable behavior, successors and prohibited evidence remain absent.
