## Context

Affected v6 began from exact published authorization and retained valid RED
chronology. Its first review exposed three blockers; the sole repair closed
scheduler/authority and connected-guard proof, but cycle 2 showed that the
default installed-origin allowlist used every value from `sysconfig.get_paths()`.
Because entries such as `scripts`, `data`, `stdlib` and `include` are not Python
package installation roots, an otherwise exact environment could be falsely
admitted. The exhausted v6 payload remains unpublished and forensic-only.

## Goals / Non-Goals

**Goals:**

- Define one exact effective-interpreter origin source: resolved `purelib` and
  `platlib` values only.
- Make default-path over-admission observable with connected neighboring
  fixtures, without relying on an injected allowlist.
- Preserve every v6 criterion already proven green and bind a clean v7 lineage.
- Authorize only a later docs-only authorization card, not implementation here.

**Non-Goals:**

- Reading, copying, repairing, committing or publishing terminal v6 payload.
- Creating v7 authorization/implementation or certification cards in this change.
- Running history, real release profiles, benchmarks, live matrix or certification.
- Changing dependency pins, scheduler behavior, CI ownership or authority rules.

## Decisions

### Exact package-root keys

The future implementation MUST request only `purelib` and `platlib` from the
effective interpreter's `sysconfig` projection. Each value is resolved fail
closed and the admitted set is the deduplicated set of those exact real paths.
No iteration over all mapping values is allowed. This is preferred over a broad
prefix test because an existing `scripts` or `data` directory is not evidence
of package installation.

### Exact distribution and executable binding

Every parsed runtime/dev pin retains its own exact file surface. The installed
distribution `locate_file("")` result MUST resolve exactly to one admitted
package root. Ruff additionally keeps its exact `0.6.9` framed version and its
executable in the selected Python bin directory. Missing keys, symlinks,
resolution faults, wrong types and ambiguous roots fail before any mutation.

### Production-default connected proof

Focused proof MUST exercise the same default root derivation used by production.
One happy neighbor returns exact `purelib`/`platlib`; independent counterexamples
place otherwise exact distribution metadata under `stdlib`, `platstdlib`,
`scripts`, `data`, `include` and an arbitrary existing path. An explicit test
allowlist can support narrow unit setup but cannot count as the default-path
acceptance proof.

### Clean lineage

The only permitted order is this docs-only decision, a separately reviewed
authorization v7, clean implementation v7 from its publishing HEAD, then the
existing certification. The future authorization carries the single six-field
bounded authorization object declared by the card; future implementation uses
only its exact two-field authorization reference.

## Risks / Trade-offs

- **Risk: platform aliases make `purelib` and `platlib` identical.** → Resolve
  and deduplicate the two exact values; equality is valid, absence or ambiguity
  is not silently replaced by another key.
- **Risk: broad prefix membership reintroduces over-admission.** → Require exact
  origin equality and a connected non-package child/root counterexample.
- **Risk: tests pass only through injected roots.** → Require at least one
  production-default derivation fixture and mutants of the actual derivation.
- **Risk: rescue scope grows into another implementation.** → Production,
  tests, CI, successors and runtime evidence remain absent and forbidden.

## Migration Plan

1. Publish this docs-only decision from exact safe authorization v6 SHA.
2. Publish a docs-only v7 authorization carrying the exact six-field object.
3. Build v7 clean from that authorization HEAD with new test-first evidence.
4. Run certification only after v7 implementation publishes.

Rollback is the published v6 authorization tip; terminal v6 remains unpublished.

## Open Questions

None. The remaining blocker and allowed root set are closed by this decision.
