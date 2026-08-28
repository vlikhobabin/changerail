## Context

Published affected-profile v10 authorization is the latest safe executable
lineage point. Its clean implementation remained unpublished after review cycle
1, the sole bounded repair, and cycle 2 (`7/9`, two blockers, rescue budget
`1/1/0` exhausted). Only those concise outcomes cross into this decision; the
terminal card, source, tests, specs, manifests, logs and raw evidence remain
forensic-only.

The unresolved class has two coupled parts. Aggregate admission did not prove
that the scheduler runtime root was a usable dedicated directory before any
mutation. The connected proof catalog could also declare itself complete while
omitting that boundary and scheduler reason/cross-field rows. Published
`changerail-release-ci` requirements remain the normative source for scheduler
summary and row semantics.

## Goals / Non-Goals

**Goals:**

- Freeze a read-only, fail-closed runtime-root and per-task-root admission
  contract that precedes Git, scheduler and filesystem mutation.
- Make every valid scheduler reason tuple and every top-level/row invalid
  partition independently enumerable before an executable catalog exists.
- Preserve the accumulated selector, scheduler, CI, authority and protocol
  artifact floor while authorizing no executable work in this change.
- Establish one clean future order and a future implementation ceiling of at
  most 499 production LOC.

**Non-Goals:**

- No repair, publication or reuse of terminal v10.
- No v11 authorization card, implementation card, focused test, production,
  CI or executable main-spec mutation.
- No reachable-history scan, real full or affected execution, benchmark, live
  matrix or certification check.

## Decisions

### 1. Dedicated runtime root is an exact descriptor, not any contained path

Future v11 admits the runtime root as the exact repository-relative output
declared by the frozen target inventory. Its leaf is one non-empty ASCII token
of at most 128 encoded bytes, starts with an alphanumeric character, contains
only alphanumeric characters plus `._-`, and is neither `.` nor `..`. NUL,
surrogate/non-encodable input, absolute input, multiple components, repository
root, lexical/real escape and any alternate leaf fail admission.

The resolved repository root, every existing ancestor, parent and leaf are
checked read-only. Ancestors and an existing leaf must be real non-symlink
directories with required search/read/write access. A missing leaf is allowed
only as the exact direct child of its real non-symlink, contained,
writable/searchable parent. A regular file, special file, symlink, inaccessible
or non-dedicated target fails the aggregate before Git, `run_plan`, `mkdir`,
`mkdtemp`, file creation or other state mutation.

This is stricter than accepting any repository-contained path: containment is
necessary, but exact descriptor identity and dedicated-leaf shape are also
required.

### 2. Every selected task root receives read-only pre-reservation proof

Before `run_plan`, future v11 evaluates every selected task root against the
same exact token grammar and the admitted runtime root. The aggregate proof
requires unique roots, direct-child lexical and resolved containment, and
absence of every candidate leaf, symlink or filesystem conflict. All rows are
checked even when an earlier row fails, and any error produces one bounded
aggregate failure with `semantic_started: 0`.

The check is intentionally pre-reservation, not a claim that races disappear.
The scheduler remains the reservation owner. A race after admission, atomic
reservation failure or conflicting creation must fail closed through the
scheduler, leave no publication authority and clean up only roots it created.

### 3. The scheduler matrix has two independent normative sources

The future focused proof must not derive expected coverage from its executable
mutation catalog. A frozen requirement-to-row map independently enumerates
top-level/schema rows, every row field partition and each reason identifier.
Separately, an immutable reason schema declares the complete valid tuple
families:

| Family | Reasons | Required tuple |
| --- | --- | --- |
| completed | `completed` | `pass`, return code `0`, output `0..8192`, cleanup `true`, messages `3` |
| terminal | `child_failed` | `fail`, nonzero integer return code, output `0..8192`, cleanup `true`, messages `3` |
| terminal | `execution_timeout` | `fail`, integer return code, output `0..8192`, cleanup `true`, messages `3` |
| terminal | `output_limit` | `fail`, integer return code, output `8193`, cleanup `true`, messages `3` |
| terminal | `cleanup_incomplete` | `fail`, null or integer return code, output `0..8193`, cleanup `false`, messages `3` |
| terminal | `internal_error` | `fail`, null or integer return code, output `0..8192`, boolean cleanup, messages `3` |
| outer | `protocol_error`, `broker_lost`, `outer_timeout`, `outer_cleanup_error` | `fail`, null or integer return code, output `0`, cleanup `false`, messages `0..2` |
| synthetic | `supervisor_result_error`, `supervisor_error`, `executor_error` | `fail`, null return code, output `0`, cleanup `false`, messages `0` |
| cancelled | `cancelled` | `fail`, null return code, output `0`, cleanup `true`, messages `0` |

For every reason, canonical neighbors cover each allowed nullable/boolean
alternative and every numeric lower, interior and upper boundary relevant to
that tuple. The independent requirement map also requires one-field mutants
for field-set, `id`, `status`, `reason`, `returncode`, `output_bytes`,
`cleanup_complete` and `messages`: wrong JSON type (including boolean-as-int),
missing/extra, unknown or empty value, lower/upper bound breach and a value
valid for another reason but invalid for the selected reason. Reason text is
non-empty ASCII token text of at most 64 encoded bytes.

Top-level rows independently cover the exact field set
`{version,status,jobs,results}`, exact version, jobs exact integer equal to the
requested `1` or `4`, status derived from all-pass versus any-fail rows,
canonical size at and above 64 KiB, result count, exact planned identity,
registry order, and missing/extra/duplicate/unknown/reused/cross-ID rows.

The executable catalog must equal the requirement-to-row set in both
directions and bind every row to a unique non-noop production-source/AST mutant,
a valid canonical neighbor, and public `profile.main` or `run_smoke`
observation after preceding guards pass. Missing, extra, duplicate or reused
rows; untested valid tuples; accepted one-field mutants; masked faults;
replacement production functions; or private-helper-only observation fail
closed.

### 4. v11 remains a sequential clean lineage

The only future order is this published investigation, a separate docs-only
`authorize-bounded-affected-release-profile-v11`, a clean
`implement-bounded-affected-release-profile-v11`, then
`certify-accelerated-release-loop-v1`. Authorization v11 must bind only that
exact successor and permit a ceiling no greater than 500; the implementation
itself may add at most 499 production LOC and must reconstruct from published
sources without terminal v10 material.

## Risks / Trade-offs

- **[Risk] Read-only admission cannot eliminate filesystem races.** → Preserve
  scheduler-owned atomic reservation and treat any post-check conflict as a
  bounded non-authoritative failure.
- **[Risk] A large mutation catalog can still omit rows by copying its own
  inventory into the oracle.** → Require bidirectional equality against a
  separately authored normative map plus the immutable reason schema.
- **[Risk] Boundary representatives can accidentally miss inclusive limits.** →
  Require lower/interior/upper valid neighbors and just-outside invalid values
  for every numeric range, plus boolean-as-integer type mutants.
- **[Risk] Another patch could silently widen the lineage.** → Keep all v11
  executable artifacts absent until the investigation and separate
  authorization are each reviewed and remotely published.
