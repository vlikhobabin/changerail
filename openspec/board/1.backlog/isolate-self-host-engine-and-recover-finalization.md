# Изоляция engine и восстановление self-host финализации

## Status
1.backlog

## Lifecycle
openspec-v1

## OpenSpec Stage
proposal

## Summary
ChangeRail при изменении собственного ядра смешивает identity исполняемого runtime
с изменяемым продуктом. После completed groups это блокирует штатный review;
ранний runtime-repair и capacity recovery не разрешают такой переход. Требуется
отдельный контракт pinned engine и явного self-host recovery до первого review.

## Acceptance
- [C1] При изменении runtime-файлов продукта runner и вложенные команды продолжают использовать один закреплённый engine; drift самого engine, профиля или launcher блокирует исполнение.
- [C2] Явный prepare/apply/reconcile сохраняет полный predecessor inventory и связывает accepted plan, исходный manifest, corrective delta и проверенный engine.
- [C3] Создаётся один successor с тремя сохранёнными completed groups и прежним расходом review; все новые gates получают свежие proofs.
- [C4] Successor начинает finalize без replay групп и проходит штатные review/archive/final/publish; сбой и обычный resume сохраняют ту же engine identity и accounting.
- [C5] Live, operator-interrupted, unresolved-verification, foreign, symlink, plan drift, review/final/archive/publish boundaries отклоняются; duplicate/race/crash не создают второго writer.

## Scope
- `scripts/changerail/`: runtime resolution, execution identity, recovery receipts и lifecycle integration.
- `bin/chrl`, `bin/chrl-run`, `bin/openspec`: вложенные команды используют закреплённый engine.
- `tools/changerail/`: schemas, skills и регрессии нового контракта.
- `docs/`: отдельный runbook self-host recovery.

## Non-Goals
- Не расширять capacity recovery до finalize или произвольной смены runtime.
- Не переписывать старые runs/receipts и не добавлять review allowance.
- Не восстанавливать автоматически отменённые карточки, operator-stopped runs, archive/final/publication.
- Не переносить настройки потребителей или provider/auth данные в публичный runtime.
- Не менять продуктовый scope текущей принятой карточки recovery.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `isolate-self-host-engine-and-recover-finalization`

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Design
- Отдельный immutable engine snapshot и project execution inputs; env path без receipt не является authority.
- Prepare связывает точный predecessor и corrective payload; apply создаёт единственный successor.
- Старое evidence сохраняется как история; изменённый payload проходит свежую проверку через штатный runner.
- Сначала нужны отдельный полный OpenSpec plan и проверка нового контракта, затем применение к реальному run.

## Delivery Budget
- primary_invariant: one byte-proven self-host successor with an immutable execution engine
- expected_wall_minutes: 180
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 15
- estimated_production_loc: 1500

## Verify
- Запланированы regression tests из acceptance, synthetic native lifecycle с локальным remote, strict OpenSpec validation, Ruff и diff-check.
- Планируемые проверки не являются выполненным evidence.
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "self-host engine and recovery",
      "precondition": "retained stopped native run and pinned engine candidate",
      "action": "exercise the matching scoped regression",
      "expected": "При изменении runtime-файлов продукта runner и вложенные команды продолжают использовать один закреплённый engine; drift самого engine, профиля или launcher блокирует исполнение.",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "self-host engine and recovery",
      "precondition": "retained stopped native run and pinned engine candidate",
      "action": "exercise the matching scoped regression",
      "expected": "Явный prepare/apply/reconcile сохраняет полный predecessor inventory и связывает accepted plan, исходный manifest, corrective delta и проверенный engine.",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "self-host engine and recovery",
      "precondition": "retained stopped native run and pinned engine candidate",
      "action": "exercise the matching scoped regression",
      "expected": "Создаётся один successor с тремя сохранёнными completed groups и прежним расходом review; все новые gates получают свежие proofs.",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C4",
      "seam": "self-host engine and recovery",
      "precondition": "retained stopped native run and pinned engine candidate",
      "action": "exercise the matching scoped regression",
      "expected": "Successor начинает finalize без replay групп и проходит штатные review/archive/final/publish; сбой и обычный resume сохраняют ту же engine identity и accounting.",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C5",
      "seam": "self-host engine and recovery",
      "precondition": "retained stopped native run and pinned engine candidate",
      "action": "exercise the matching scoped regression",
      "expected": "Live, operator-interrupted, unresolved-verification, foreign, symlink, plan drift, review/final/archive/publish boundaries отклоняются; duplicate/race/crash не создают второго writer.",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    }
  ],
  "risks": [
    {
      "kinds": [
        "input_safety",
        "mutation",
        "restart",
        "concurrency"
      ],
      "applies": true,
      "decision": "exact manifests, immutable inventories, validated engine routing, project lock and atomic successor",
      "conditions": [
        "C1",
        "C2",
        "C3",
        "C5"
      ]
    },
    {
      "kinds": [
        "publication",
        "external_effects"
      ],
      "applies": true,
      "decision": "migration grants no publication authority; successor uses normal review/final/publication gates; integration tests use local fixture remotes",
      "conditions": [
        "C4",
        "C5"
      ]
    }
  ]
}
```

## Result
Подготовлен отдельный объём работ. Реализация и принятие плана не начаты.
Локальный технический проект сохранён в `.runtime/changerail/self-host-recovery-design/proposal.md`;
он не является recovery receipt.

## Next
- Подготовить и проверить отдельный native OpenSpec plan, затем принять его перед реализацией.

## Log
- 2026-09-10T19:08:24Z Карточка создана по post-stop audit текущей self-host доставки; текущий accepted plan и retained run сохранены.
