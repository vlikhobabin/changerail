## Context

Published authorization v14 is the latest safe executable frontier. Its clean
successor remained unpublished after cycle 1 `NO-GO`, one bounded repair and
cycle 2 `NO-GO`; only the validated cycle summaries are inputs here. Cycle 2
showed that resolving expected tools from live `PATH` at module import merely
freezes an attacker-controlled value, while a large source-mutant count can
remain non-discriminating when cases reuse the same weakened guard or assert
only a safety-floor subset.

The accumulated release contract still requires exact 35-ID semantics,
35-to-30 physical ownership, full-only authority, four public Git streams,
typed scheduler summaries, source-safe CI and final certification. V15 must
simplify how identity and proof are established without weakening those
behaviors.

## Goals / Non-Goals

**Goals:**

- derive canonical executable origins without using live `PATH` as expected
  truth;
- reject a usable fake present before import and before any probe or semantic
  mutation;
- make every source mutant a distinct semantic edit whose public behavior is
  observed from an exact passing neighbor;
- reject scheduler aliases and prove exact A/M/D plus both R/C operand owners;
- publish a bounded authorization/implementation path to final certification.

**Non-Goals:**

- repair or publish terminal v14;
- reuse v14 code, tests, card, specs, manifests, logs or raw evidence;
- change scheduler/supervisor semantics, inventory size or authority rules;
- run history, full/affected release execution, benchmark, live matrix or
  certification during investigation.

## Decisions

### 1. Expected origin comes from typed source anchors, never live PATH

V15 will own one immutable `OriginDescriptor` tuple per executable token. A
descriptor names its role, one anchor kind, exact relative target and symlink
policy. Anchor kinds are closed:

- `repository-root`: exact admitted repository root for repo launchers;
- `effective-interpreter`: real `sys.executable`, never `which("python3")`;
- `interpreter-scripts`: exact real `sysconfig.get_path("scripts")` for Ruff;
- `platform-toolchain`: a source-authored per-platform/per-token table of
  generic absolute candidate targets or an explicitly admitted setup-toolchain
  root whose lexical and real containment are independently validated.

The canonical resolver enumerates only descriptor targets. It does not search
or freeze live `PATH`. The current effective `PATH` result is separately
resolved and must equal the one canonical real target; zero, alternate,
ambiguous, resolving/dangling-symlink, wrong-type or inaccessible targets are
aggregate admission faults. All subprocess argv use the admitted absolute
target, so a successful fake version probe cannot upgrade identity.

Alternatives rejected: import-time `shutil.which` self-freezing accepts a fake
already present before import; version-only probes admit arbitrary compatible
programs; machine-specific absolute paths in tracked artifacts violate the
public repository boundary.

### 2. Pre-import counterexamples are child-process integration fixtures

Focused proof creates a temporary fake executable that returns the exact
expected version and would write a marker if called. A clean child receives a
`PATH` with that fake first before Python imports the public runner/profile.
The child must return one bounded non-authoritative report with zero semantic
start. The marker, Git-call ledger and runtime-root snapshot remain unchanged.
Separate clean-child cases cover Python, Ruff, Git, Node, npm, npx and the
repository OpenSpec target; sharing one anchor kind cannot replace any token
case. The cases do not patch resolver functions or expected constants in
memory.

### 3. Completeness separates data rows from semantic guard mutants

The normative requirement catalog enumerates every valid/invalid row,
top-level, origin, selector and ownership case. A separate executable catalog
maps cases to exact public observers and semantic AST edits. Completeness is the
bidirectional equality of requirement ids and executable case ids.

Mutant uniqueness is not a count. Each mutant serializes the changed canonical
AST without test-only marker nodes and records the exact changed node path,
operator and before/after digest. Two cases may exercise the same production
guard, but they cannot claim two distinct mutants from the same edit. Every
guard has at least one unique semantic mutant, and every data case still runs
independently from its reason-specific passing neighbor. This v15 definition
supersedes accumulated wording that encouraged one marker-distinguished copy
of the same guard per data row.

### 4. Scheduler ownership uses a closed import/call graph

The source oracle resolves every import and assignment that can refer to the
scheduler module or `run_plan`. It permits exactly one unaliased `ImportFrom`
and one direct `ast.Name("run_plan")` call inside the single lexical depth-one
activation statement. Alias imports, module-qualified calls, assignment
aliases, wrappers, `getattr`, dynamic dispatch, duplicate calls and alternate
runner entrypoints are explicit executable source mutants and must make the
oracle red.

### 5. Selector expectations are exact and owner-distinct

Each committed/staged/unstaged A/M/D case uses a path whose owner adds a
semantic id beyond the safety floor and asserts the exact registry-ordered
tuple. R/C cases use old and new paths with different owners and assert both
ids. Source mutants that skip a status, stream or operand must change the
public tuple and be killed. Parser-only acceptance remains supplemental; the
authoritative proof observes public selection/fallback reports.

### 6. One new clean lineage precedes certification

After this investigation is published, a docs-only authorization v15 will bind
one clean implementation at ceiling `500` (maximum `499` additions). The
implementation starts from the authorization-publishing HEAD, creates its own
genuine pre-production RED and uses only published contracts. Certification is
created only after that implementation is remotely published with fresh GO.

## Risks / Trade-offs

- **[Risk]** Platform-toolchain targets differ across Linux/macOS and CI
  setup-node layouts. → The descriptor table is per platform/token, uses only
  generic public anchors and fails closed on unsupported layouts; certification
  tests the exact supported environment.
- **[Risk]** Many data cases still map to one guard. → Completeness counts case
  ids separately from unique semantic edits and requires both bidirectional
  maps plus one behavioral kill per case.
- **[Risk]** AST alias analysis can miss a dynamic surface. → Reject all
  scheduler module imports, assignments and calls outside the one exact allowed
  form instead of trying to prove arbitrary dynamic equivalence.
- **[Risk]** Exact selector tuples couple tests to registry order. → Registry
  order is already normative identity; independently transcribed expected ids
  are the desired drift detector.

## Migration Plan

1. Publish this docs-only investigation from authorization v14 HEAD.
2. Publish a separate exact authorization v15.
3. Create a clean v15 worktree, retain a new genuine RED, implement from
   published specs and obtain fresh ordinary/high GO.
4. Publish v15, then create and run the single critical certification card.
5. If v15 fails after its bounded repair, do not patch or certify it; retain a
   terminal forensic handoff under the standard escalation policy.

Rollback before publication discards only the new docs-only worktree. No
runtime migration exists.

## Open Questions

None. Origin anchors, mutant semantics, scheduler ownership, selector
discrimination and future ordering are fixed by this decision.
