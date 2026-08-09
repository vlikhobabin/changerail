## Context

The ChangeRail repository currently has a minimal knowledge catalog and policy.
That proves validation and index rendering, but not real detector coverage over
the canonical documentation surface. The maintenance harness also needs tracked
fixtures for deterministic detector failures and an explicit boundary for
agent-authored contradiction annotations.

## Goals / Non-Goals

**Goals:**
- Expand the dogfood catalog and maintenance policy to an explicit canonical
  ChangeRail knowledge scope.
- Enable applicable built-in deterministic detectors by default for dogfood
  scans.
- Keep the generated index deterministic and current.
- Add public-safe fixtures for broken links/anchors, stale generated output,
  optional instruction producer import and contradiction annotations.
- Keep default dogfood commands read-only and independent of ignored local
  history.

**Non-Goals:**
- Do not make feedback/runtime-dependent adapters default CI dependencies.
- Do not promote semantic contradiction from agent annotation to deterministic
  failure.
- Do not implement instruction-budget thresholds or producer semantics owned by
  card `050`.
- Do not introduce private repository names, paths, traces or credentials.

## Decisions

1. Dogfood scope stays explicit in tracked policy.

   `.changerail/maintenance.yaml` declares include/exclude globs and enabled
   detectors. The default command stays read-only; generated index updates still
   require explicit `render-index --write`.

2. Fixtures exercise failure cases outside the clean root scan.

   Broken link/anchor and stale generated output fixtures live under
   `fixtures/repository-knowledge/`. Smoke tests run them in controlled fixture
   workspaces so the repository root can stay clean and pass dogfood scan.

3. Instruction metrics remain optional.

   Dogfood rollup reports instruction bytes as `unknown` until card `050`
   publishes a producer. Any fixture for instruction producer import validates
   schema-bound optional input behavior and does not create a temporary
   threshold.

4. Semantic contradiction is annotation-only.

   Agent contradiction evidence can be retained as maintenance annotation or
   proposal evidence, but one model verdict is not a deterministic scan gate.

## Risks / Trade-offs

- [Risk] Enabling link detectors over too broad a scope may surface unrelated
  historical links.
  Mitigation: the policy uses explicit canonical include/exclude globs.
- [Risk] Generated index drift can create noisy failures.
  Mitigation: index updates remain deterministic through the existing renderer
  and are checked in smoke tests.
- [Risk] Agent annotations can be mistaken for deterministic proof.
  Mitigation: fixtures and specs keep contradiction annotation separate from
  scan detector failures.

## Migration Plan

Update the tracked dogfood catalog, policy and generated index together. Add
fixtures and smoke assertions before making root dogfood scan part of the
verification floor for this card.

## Open Questions

- none
