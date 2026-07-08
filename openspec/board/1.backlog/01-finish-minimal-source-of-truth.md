# Завершить минимальный source of truth (Фаза 1)

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- OPSX roadmap, раздел 12, Фаза 1 (`docs/opsx-source-of-truth-architecture.md`).
- Path-neutrality и контрактный namespace (раздел 7).

## Summary
Довести Фазу 1 до состояния, когда OPSX может быть полноценным источником
symlink-ов: перенести оставшиеся generic lifecycle skills, `openspec-*` skills,
wrapper `bin/openspec`, review-verdict helper и контрактные `schemas/` в
namespace `opsx.*`. Каждый переносимый skill должен быть path-neutral и без
упоминаний legacy-workspace.

## Acceptance
- `skills/opsx-do`, `skills/opsx-review`, `skills/opsx-pub`, `skills/opsx-deliver`
  существуют, path-neutral, описывают generic lifecycle без domain-specific
  provider/trace политики.
- `openspec-*` lifecycle skills присутствуют; зафиксированы источник, лицензия и
  политика синка с развитием OpenSpec CLI.
- `bin/openspec` wrapper присутствует, pin версии CLI + compatibility notes.
- `schemas/` содержит review-verdict, delivery-manifest и evidence-index в
  namespace `opsx.*`; validate/fingerprint helper-ы достижимы.
- review-verdict helper присутствует и генерирует контрактный verdict.
- Все перенесенные skills path-neutral (нет machine-specific fallback-путей и
  legacy-workspace имен); контрактные id — на `opsx.*` (legacy-семейство
  принимается helper-ами как deprecated на переходный период).
- OpenSpec validation и public-surface scans проходят.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `AGENTS.shared.md`
- `skills/opsx-explore/SKILL.md`
- `skills/opsx-ff/SKILL.md`
- `docs/wiring-discovery.md`

## Result
not started

## Next
- triage: перенести карточку в `2.todo` и через `opsx-ff` разложить на ordered
  changes (ориентировочно: lifecycle skills; `openspec-*` skills + `bin/openspec`;
  contracts/schemas + helper).

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.).

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 1 remaining scope.
