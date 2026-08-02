## Context

The `040-native-windows-implementation` epic and cards were created before
`030-02` captured runtime/wiring evidence and before `030-03` selected the
architecture. They therefore describe provisional symlink, wrapper and smoke
work without a final default/fallback model.

This change refreshes only the board planning surface. It does not implement
Windows shims, generated-copy wiring, verification checks or live smoke
automation.

## Goals / Non-Goals

**Goals:**
- Rewrite the `040` epic as an executable implementation sequence against the
  selected `030-03` architecture.
- Keep the series as five publishable story cards with clear dependencies:
  entrypoints, wiring backend, verification/Git safety, smoke matrix and
  end-to-end proof.
- Replace provisional acceptance text with concrete acceptance and verification
  expectations.
- Keep all `040` executable stories in `1.backlog` until individually moved
  through readiness gates.

**Non-Goals:**
- Generate OpenSpec artifacts for `040` cards.
- Move any `040` story to `2.todo`.
- Implement runtime, bootstrap, verifier, drift or smoke code.

## Decisions

1. Keep the five-card series shape.
   - `040-01` implements `.cmd` entrypoints and runtime invocation semantics.
   - `040-02` implements generated-copy Windows wiring and explicit fallbacks.
   - `040-03` implements verifier, drift and Git safety gates.
   - `040-04` turns research probes into automated native Windows smoke.
   - `040-05` proves clean-clone end-to-end support and final docs.
   - Alternative rejected: merge all implementation into one broad card; the
     architecture spans commands, generated files, verification, smoke and
     release docs and needs independently reviewable gates.

2. Runtime entrypoints come before wiring.
   - Bootstrap and verifier cannot reliably invoke helper surfaces on Windows
     until native command wrappers and Python/OpenSpec invocation behavior are
     defined and tested.

3. Verification and Git safety follow wiring backend implementation.
   - The verifier and drift gate need the final generated ownership model and
     fallback semantics before they can enforce fail-closed behavior.

4. End-to-end proof remains last.
   - E2E validation should consume the implemented wrappers, wiring backend,
     verifier, smoke matrix and docs instead of substituting ad hoc probes.

## Risks / Trade-offs

- [Risk] The refreshed cards may still be too large once implementation starts.
  Mitigation: each card remains in `1.backlog`; `ff` for each card can split
  into smaller OpenSpec changes before delivery.
- [Risk] Test-matrix work depends on operator-managed Windows hosts.
  Mitigation: each affected card requires deterministic local fixtures and
  records explicit blockers when live-host evidence is unavailable.
- [Risk] Backlog refresh could drift from the architecture spec.
  Mitigation: acceptance and verification in every card reference the
  `030-03` architecture decision and fail-closed support contract.
