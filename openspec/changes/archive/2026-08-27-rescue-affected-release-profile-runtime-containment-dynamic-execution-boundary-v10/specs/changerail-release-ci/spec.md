## ADDED Requirements

### Requirement: Affected v10 rescue MUST publish a clean runtime and execution-ownership decision
ChangeRail MUST publish
`rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10`
docs-only from exact safe affected v9 authorization commit
`9c27bd9fd52f7760ddf3d1d6115abca88e3670e9`. Terminal unpublished v9 code,
tests, specs, manifests, logs and raw evidence MUST remain forensic-only; only
its concise validated cycle counts and blocker summaries MAY cross the clean
lineage boundary.

The decision MUST contain exactly one future authorization object:
`{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10.md","investigation_id":"rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v10.md","successor_id":"implement-bounded-affected-release-profile-v10","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
It MUST add zero production, test and runtime LOC and MUST leave v10 successors
and certification absent.

#### Scenario: Exhausted v9 cannot receive another patch
- **WHEN** v9 cycle 1 and the sole repair are followed by cycle-2 `NO-GO` with
  rescue budget `1/1/0` exhausted
- **THEN** v9 remains unpublished and unmodified
- **AND** the only executable successor path is this decision, authorization
  v10, clean implementation v10 and then certification.

### Requirement: Affected v10 runtime admission MUST close real ancestor containment
Future v10 admission MUST validate the resolved repository root, every existing
runtime-output ancestor and the leaf before Git, scheduler or filesystem
mutation. Existing and missing leaves MUST reject lexical or resolved escape,
symlinked leaf/ancestor, wrong type and insufficient access. A final-leaf-only
type/access check MUST NOT establish repository containment.

#### Scenario: Existing directory resolves through an outside symlink
- **WHEN** a lexically repository-local runtime leaf exists through any
  symlinked ancestor or resolves outside the real repository root
- **THEN** aggregate admission reports a bounded containment error with
  `semantic_started: 0`
- **AND** Git selection, scheduler activation and filesystem mutation do not run.

#### Scenario: Real contained output neighbor passes
- **WHEN** every ancestor is a real contained directory and the leaf is either
  a valid real directory or a missing direct child of a valid writable parent
- **THEN** runtime containment contributes no admission error
- **AND** all unrelated admission guards still run before semantics.

### Requirement: Affected v10 ownership MUST inventory every import and call shape
The source ownership oracle MUST parse actual runner, profile and scheduler
source and compare the exact normalized inventory of every import and every
`ast.Call`, including file, enclosing scope, structural callee form, positional
arity and keyword names. Only the frozen direct runner → profile → scheduler →
broker chain and declared scheduler infrastructure calls MAY pass.

Aliases, star/module imports, rebinding, wrappers, dynamic imports,
`__import__`, `importlib`, `getattr`, `globals`, `locals`, `vars`, subscript or
call-result callees, attribute indirection and every extra raw/semantic
execution site MUST fail even when every canonical direct call remains.

#### Scenario: Dynamic call preserves the canonical chain
- **WHEN** copied actual source adds a dynamic runner profile call, dynamic
  profile scheduler call, subscripted `_probe` call or dynamic broker call
- **THEN** public `run_smoke` fails the exact call/import inventory
- **AND** no visually canonical preserved call can mask the alternate site.

### Requirement: Affected v10 proof MUST cover the complete normative guard catalog
Future v10 focused proof MUST contain one finite immutable catalog covering
every typed operand/target missing/type/access/containment guard, Python/Ruff
and each distribution origin, real `purelib`/`platlib` and runtime ancestor
case, resolved base and all four Git streams, every status/path/framing/count/
per-stream/aggregate bound, scheduler top-level/row/order/status/size and every
reason cross-field, affected/full authority, receipt/capture/marker/cache and
all ownership/import/call surfaces.

Every catalog row MUST bind one unique guard id, a passing canonical neighbor,
one exact non-noop actual-source/AST mutation, a public `profile.main` or
`run_smoke` observation and proof that real preceding guards passed. Missing,
extra, duplicate or reused rows, runtime replacement of production functions,
private-helper-only observation and earlier-fault masking MUST fail focused
verification.

#### Scenario: Catalog defines and executes complete proof
- **WHEN** focused verification runs in isolated subprocess/repository fixtures
- **THEN** every normative guard row executes its canonical and single-mutant
  pair through the declared public observer
- **AND** the gate fails if any required row is omitted or any mutation is
  accepted, disconnected, no-op, masked or dependent on function replacement.

### Requirement: Affected v10 lineage MUST preserve the accumulated release floor
Future authorization v10 MUST depend exactly on this rescue, the integration
decision, scheduler v1 and affected v9 authorization and MUST block only
implementation v10. Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v10.md","authorization_id":"authorize-bounded-affected-release-profile-v10"}`,
depend exactly on this rescue, integration decision, scheduler v1, affected v9
authorization and authorization v10, block only certification, start from the
authorization-publishing HEAD and add at most 499 production LOC.

Future v10 MUST retain the valid pre-production RED boundary, exact 35-ID
digest and 35→30 typed ownership, aggregate admission, strict four-stream
selection, scheduler-v1 activation, full-only authority, exact four-step CI
and protocol-artifact non-authority. This rescue stage MUST NOT run or accept
history, real full/affected, benchmark, live-matrix or certification evidence.

#### Scenario: Clean successor preserves authority and dormancy
- **WHEN** this rescue is reviewed or a future v10 card is prepared
- **THEN** the exact order, object, dependencies, sole block, LOC and accumulated
  release floor are machine-checkable
- **AND** no v10 executable work exists before separate authorization publication.
