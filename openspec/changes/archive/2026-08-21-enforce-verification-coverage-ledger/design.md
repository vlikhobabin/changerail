## Context

Предыдущий change определяет project map, per-change plan reference и runtime
ledger contracts. Текущий `changerail-ff` создает OpenSpec artifacts,
`changerail-do` формирует и обновляет delivery manifest/evidence,
deterministic review preflight валидирует process gates, а independent review
записывает acceptance verdicts. Enforcement должен связать эти существующие
phases, не добавляя еще один review result.

## Goals / Non-Goals

**Goals:**

- Make planning omissions and actual-scope drift deterministic before review.
- Bind applicable invariants to observed evidence-index entries.
- Fail closed on missing, stale or invalid ledger when a map is configured.
- Require independent reviewer to audit oracle adequacy and acceptance mapping.
- Prove the flow on one generic Python false-green fixture.

**Non-Goals:**

- Не выполнять domain tools автоматически из generic core.
- Не позволять path matching или command exit zero автоматически pass
  acceptance.
- Не изменять проекты без configured map.
- Не хранить raw evidence in tracked plan/card.

## Decisions

1. **`ff` owns planned selection.** Fast-forward reads configured map and
   planned proposal/design impact, then creates
   `openspec/changes/<slug>/verification-coverage.json`. It must include every
   rule it judges applicable and card acceptance hashes; uncertain selector
   becomes explicit planned rule, not silent omission. `ff` does not claim
   observed coverage.

2. **`do` owns actual-scope reconciliation.** Once delivery manifest has
   working-tree scope, helper deterministically matches operations/paths and any
   schema-valid extension surface report. If actual applicable ids are absent
   from plan, delivery blocks and returns to planning. Planned-but-not-actual ids
   may be marked not-applicable with scope evidence; they are not silently
   deleted.

3. **Evidence links use existing index.** For each applicable id, delivery
   records oracle state and `evidence_refs` pointing to
   `changerail.evidence-index.v1` entries. Required kinds, oracle ref, pass
   status, scope and freshness are validated. Raw output remains ignored.
   Manifest gets only concise ledger path/fingerprint/status summary.

4. **Deterministic preflight checks freshness and completeness.** Preflight
   validates map and plan at tracked `HEAD`, current card/manifest/review
   fingerprint, applicability reconciliation and required evidence refs. Any
   missing or stale applicable entry is a process blocker before LLM review and
   consumes no review cycle.

5. **Reviewer still judges adequacy.** Review skill reads map entry, linked
   evidence and exact acceptance criteria. It must identify whether oracle
   observes the published boundary and whether test could fail for the claimed
   regression. A complete ledger with disconnected paths or wrong boundary
   becomes blocker finding; ledger does not self-authorize `pass`.

6. **False-green proof covers three shapes.** Synthetic Python fixture includes
   missing positive route, assertion against an internal timeout helper rather
   than public API, and integration proof where producer/consumer paths are not
   connected. RED proves current floor can appear green; GREEN proves planning
   or preflight/review detects each gap.

7. **Skills are canonical source.** Update canonical ChangeRail skills and
   their short aliases/wrappers through existing source/symlink conventions;
   generated consumer guidance is updated and drift-checked.

## Risks / Trade-offs

- [Agent planning selection remains semantic] -> actual deterministic matcher
  catches rules omitted for changed paths/surface ids before review.
- [Evidence id exists but oracle is weak] -> reviewer adequacy remains required;
  process gate checks identity/freshness, not semantic truth.
- [Large map slows preflight] -> parse once, deterministic bounded matching,
  no command execution during selection.
- [Stale plan after card edit] -> acceptance/map fingerprints fail closed.

## Migration Plan

1. Add map/plan/ledger helper and manifest summary field.
2. Update `ff` and `do` flows.
3. Add preflight/reviewer enforcement.
4. Add generic RED/GREEN and no-map compatibility fixtures.
5. Update shared methodology/templates/docs; rollback ignores optional config
   and removes generated ledger without touching existing evidence.

## Open Questions

- none
