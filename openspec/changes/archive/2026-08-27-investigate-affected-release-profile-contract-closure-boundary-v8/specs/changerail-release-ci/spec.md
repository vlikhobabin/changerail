## ADDED Requirements

### Requirement: Affected v8 investigation MUST replace terminal unpublished affected v7
ChangeRail MUST publish
`investigate-affected-release-profile-contract-closure-boundary-v8` as one
docs-only investigation/design decision from exact published
`authorize-bounded-affected-release-profile-v7` tip
`72541e3e9e906000922829629026d45bc77ae078`.

The terminal unpublished v7 implementation, code, tests, card, manifest,
verdict files, logs and evidence MUST remain forensic-only and MUST NOT be
read, copied, cherry-picked or accepted by a future implementation gate. The
decision MAY retain only the concise chronology: cycle 1 and cycle 2 were both
`NO-GO` at `9/12`; the sole repair was consumed; registry admission, exact
ownership and connected proof remained blockers.

The only future order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v8`, clean
`implement-bounded-affected-release-profile-v8`, then
`certify-accelerated-release-loop-v1`. The future authorization MUST contain
exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-contract-closure-boundary-v8.md","investigation_id":"investigate-affected-release-profile-contract-closure-boundary-v8","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v8.md","successor_id":"implement-bounded-affected-release-profile-v8","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Authorization v8 MUST depend exactly on this decision,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v7`, and MUST block only
implementation v8. The clean implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v8.md","authorization_id":"authorize-bounded-affected-release-profile-v8"}
```

It MUST depend exactly on the five predecessors declared by this decision plus
authorization v8, block only certification, start from authorization-publishing
HEAD and add at most 499 production LOC.

#### Scenario: Repeated blockers force investigation before implementation
- **WHEN** terminal v7 has exhausted its sole same-card repair and repeated admission or proof blocker classes remain
- **THEN** ChangeRail publishes this docs-only decision and a separate authorization before any clean v8 implementation exists.

### Requirement: Affected v8 MUST derive one exhaustive typed target inventory
Future v8 MUST use one frozen immutable typed registry as the authoring
source-of-truth for all 30 physical tasks and non-task targets. Every execution
operand MUST have exactly one declared kind from `executable`, `module`,
`script`, `file`, `directory` and `embedded-command`, plus a normalized
repository-relative identity when that kind is repository-owned.

Before Git selection, scheduler activation or filesystem mutation, admission
MUST independently extract the typed operand multiset from every physical task
and compare it with the frozen registry. Path suffix, slash presence,
filesystem existence or another path-shape heuristic MUST NOT infer kind.
Missing, extra, duplicate-ambiguous, repository-root, absolute, escaped,
symlink-substituted, wrong-type or wrong-kind operands MUST yield one bounded
fault report with `semantic_started: 0`.

The inventory MUST include nested/embedded command operands and every frozen
file/directory target. It MUST validate executable and module availability,
exact file/directory type and repository containment, while preserving exact
pins and effective-interpreter `purelib`/`platlib` origin admission.

#### Scenario: Every physical operand has one typed admission result
- **WHEN** a physical command adds, removes, duplicates, embeds, retypes or redirects any operand
- **THEN** aggregate admission detects the exact inventory mismatch before Git, scheduler or filesystem mutation instead of accepting it through shape inference.

### Requirement: Affected v8 MUST close import binding and semantic execution ownership
The source-safe ownership oracle MUST bind each authorized import to its exact
loaded name and exact call site. The runner MUST have one unaliased profile
`main` import and one canonical guarded `main(sys.argv[1:])` call; the profile
MUST have one unaliased scheduler `run_plan` import and one canonical call; the
scheduler MUST have one unaliased broker activation import and one canonical
call.

Star imports, module imports, aliases, shadowing, assignment or definition
rebinding, wrappers, attribute calls, duplicate calls and calls outside the
authorized guard/function MUST fail closed. Merely finding one canonical import
and one same-spelled call MUST NOT satisfy binding ownership.

The oracle MUST also maintain a closed raw execution-site inventory. Semantic
commands MUST execute only through the typed scheduler chain. Any additional
module-qualified call, individual semantic command, `subprocess`, `os.system`,
`exec`/`eval` or equivalent direct/indirect wrapper outside the exact admitted
sites MUST fail, even when the canonical chain remains present. Canonical CI
MUST remain exactly four source-safe steps and invoke only
`python3 scripts/run-release-baseline.py --profile full-release`.

#### Scenario: Parallel indirect execution cannot hide beside canonical calls
- **WHEN** a source mutant keeps every canonical import and call but adds an alias, rebound symbol, module-qualified call or extra individual process execution
- **THEN** the ownership oracle fails because binding or the closed execution inventory changed.

### Requirement: Affected v8 MUST prove every guard with a connected source mutant
Future v8 focused proof MUST cover every required target, origin, selector,
runtime, scheduler, authority, protocol-artifact and ownership/execution guard.
Each proof MUST start from a
passing canonical neighbor, apply one bounded non-noop source or AST mutation
to the actual production guard, load that mutated production source in an
isolated fixture and observe the changed result through the public runner or
oracle boundary.

The fixture MUST prove that all preceding guards are satisfied and that the
intended guard is reached. Patching the guard function, overriding its constant
or return value, reimplementing the assertion locally, mutating only test data
that an earlier fault rejects, or inspecting an internal disconnected helper
MUST NOT count as connected proof. Every named mutant MUST change only its
intended observable guard outcome.

The finite inventory MUST cover every typed target kind and operand class,
effective package origins, resolved-base and all path/count/stream/aggregate
bounds, runtime-output order/type, every scheduler summary/row/status/reason
cross-field, full-only authority, every protocol-artifact state and every
forbidden import/call/execution surface.

#### Scenario: Disconnected mocks cannot satisfy proof coverage
- **WHEN** a focused test patches a guard or triggers an earlier fault without mutating and reaching the actual production guard
- **THEN** verification marks that required counterfactual unproved and blocks review handoff.

### Requirement: Affected v8 investigation MUST preserve the v7 floor and remain dormant
The future v8 contract MUST preserve retained pre-production RED chronology,
exact 35-ID digest and 35→30 ownership, effective-interpreter package origins,
aggregate pre-mutation admission, strict committed/staged/unstaged/untracked
NUL selection and all bounds, scheduler-v1 sole activation and closed typed
rows, full-only authority, exact source-safe four-step CI and protocol-artifact
non-authority.

This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` main specification and archive metadata.
It MUST add production/test/runtime LOC `0`, create no authorization,
implementation or certification successor, and run or accept no reachable
history, real full baseline, real affected execution/benchmark, live matrix or
certification evidence.

#### Scenario: Investigation changes contract without activating release work
- **WHEN** maintainers plan, deliver, review or publish this decision
- **THEN** only docs/spec artifacts change while executable, successor and prohibited evidence surfaces remain absent.
