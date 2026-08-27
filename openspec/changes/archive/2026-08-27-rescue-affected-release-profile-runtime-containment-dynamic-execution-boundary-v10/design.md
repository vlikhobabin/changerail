## Context

Affected profile v9 is terminal and unpublished. Its first review found typed
operand, ownership-oracle and proof-completeness gaps. One bounded repair closed
the literal examples, but fresh cycle 2 still reproduced an existing runtime
leaf outside the repository through a symlinked ancestor, four dynamic
execution bypasses and missing/disconnected proof rows. The same-card budget is
exhausted, while the latest safe public state remains authorization v9 at
`9c27bd9fd52f7760ddf3d1d6115abca88e3670e9`.

## Goals / Non-Goals

**Goals:**

- publish a clean-room decision before any v10 executable work;
- make realpath containment cover existing and future runtime outputs plus all
  ancestors before mutation;
- replace narrow dangerous-call matching with a closed normalized AST call and
  import inventory for runner, profile and scheduler;
- make the normative guard catalog finite, complete and executable through a
  public boundary with real preceding guards;
- retain the 35-ID/30-task, selector, scheduler, authority and CI contract.

**Non-Goals:**

- reuse or repair terminal v9 code, tests, specs or raw runtime evidence;
- implement or authorize v10 in this change;
- change scheduler/broker semantics, publication authority or certification;
- run history, real full/affected, benchmark, live or certification evidence.

## Decisions

### Clean lineage and exact order

The decision uses only published contracts and concise validated review
findings. Terminal v9 remains forensic-only. The sole order is rescue decision,
docs-only authorization v10, clean implementation v10, then certification.
Authorization uses the exact six-field object in the card and permits at most
499 added production LOC from its future published HEAD.

### Containment validates the complete real path chain

Future admission treats the repository root, runtime parent chain and runtime
leaf as typed objects. For both existing and missing leaves it resolves the
nearest existing ancestor strictly, rejects every symlink component, requires
the resolved ancestor/leaf to be relative to the resolved repository root,
checks exact directory type and required access, and only then permits
scheduler mutation. Leaf-only `is_dir`/access checks cannot establish
containment.

The same total validator owns release-profile and drift runtime roots. A
canonical real-directory neighbor and isolated missing leaf, wrong type,
unreadable leaf, symlink leaf, symlink ancestor and outside-realpath faults are
required. Alternatives based on lexical prefix or final-leaf checks are
rejected because they reproduce the v9 escape.

### Closed normalized import and call inventory

The ownership oracle parses actual runner, profile and scheduler source and
normalizes every import plus every `ast.Call` by file, enclosing scope,
structural callee form, positional arity and keyword names. The exact frozen
inventory permits the intended direct runner → profile → scheduler → broker
chain and the scheduler's declared infrastructure calls; any missing, added,
rebound or structurally different import/call fails.

Dynamic callee forms are denied unless an exact non-semantic infrastructure
row is frozen. In particular `__import__`, `importlib`, `getattr`, `globals`,
`locals`, `vars`, subscripted callables, calls returned by other calls,
attribute/module indirection, wrappers and alternate subprocess/system/
exec/eval sites cannot coexist with a passing canonical direct chain. A narrow
name/attribute denylist was rejected because cycle 2 bypassed it four ways.

### Normative guard catalog is the proof source of truth

Future focused proof contains one immutable catalog whose exact IDs cover all
categories listed in the card/spec: typed operands and targets, interpreter and
distribution origins, package/runtime containment, Git base and four streams,
all path/status/framing/count/byte bounds, scheduler summary/rows/order/status/
size/cross-fields, authority/artifacts and every import/call surface.

Each row contains only `id`, canonical neighbor, exact source/AST mutation,
public observer and preceding-guard evidence. Tests fail on a missing/extra/
duplicate row, no-op mutation, absent source span, reused mutation or private
observer. The catalog is not inferred from the implementation's current test
list, so omission cannot define its own completeness.

### Public proof uses subprocess fixtures, not runtime monkeypatching

Canonical and mutant cases run actual copied source in isolated repository
fixtures and enter through `profile.main` or `run_smoke`. Filesystem, PATH,
pinned interpreter and import-time scheduler-result fixtures may establish the
external input, but production functions are not assigned/replaced after load.
Each pair differs by one non-noop source/AST mutation and one isolated fault;
the canonical neighbor proves every preceding guard passes before the target
guard. Both sides use the same fixture bytes. Private helper observations may
supplement diagnostics but never satisfy a catalog row.

## Risks / Trade-offs

- [The call inventory is intentionally sensitive to harmless source changes] →
  update it only through a separately reviewed ownership change; fail-closed
  sensitivity is preferable on the sole release execution chain.
- [A complete guard catalog is large] → keep executable proof in non-production
  tests/fixtures and production logic within the 499-line ceiling.
- [Isolated repository fixtures cost more than monkeypatch unit tests] → run
  only focused static/subprocess cases in implementation; real release remains
  certification-only.
- [Access behavior differs for privileged users] → use structural mode/type
  and controlled subprocess identity where access is the target guard, and
  require the canonical/fault pair to prove the observed distinction.

## Migration Plan

1. Publish this docs-only decision from exact safe authorization v9.
2. Publish a separate exact authorization v10.
3. Start v10 clean with retained pre-production RED before executable mutation.
4. Implement containment, closed AST inventory and complete catalog from
   published contracts only; run focused/static/current gates and fresh review.
5. Proceed to certification only after a published v10 implementation.

Rollback before publication removes only this card/change. After publication,
superseding the decision requires a new tracked investigation; terminal v9 is
never a rollback source.

## Open Questions

- none; the safety boundary, sequence, proof shape and prohibited evidence are
  fixed by this decision.
