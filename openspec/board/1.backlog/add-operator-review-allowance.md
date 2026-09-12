# Операторский +1 к бюджету ревью при исчерпании остатка

## Status
1.backlog

## Lifecycle
openspec-v1

## OpenSpec Stage
artifacts

## Owner
unassigned

## Source
- Разбор неопубликованной работы в dev-checkout 2026-09-12: `.runtime/planning/repo-cleanup/UNPUBLISHED-WORK-ASSESSMENT.md`.
- Поручение оператора от 2026-09-10 (отменённая карточка `5.canceled/allow-single-operator-review-extension`): дать поддерживаемый переход после двух NO-GO.
- Фактическая реализация уже существует в dev: `scripts/changerail/review_allowance.py` и интеграция в раннер.

## Summary
Первые два независимых ревью автономны и расходуют общий остаток. После
терминального NO-GO у оператора нет поддерживаемого способа разрешить ровно один
дополнительный repair и review. Реализованный контракт даёт двухфазный
`review-allow`: preview возвращает digest, `--authorize` атомарно добавляет
неизменяемую запись вне старых runs. Слот привязывается к единственному
recovery successor до появления writer и не ослабляет proofs, scope, frozen
identity и финальные гейты. Граница доверия — кооперативная в пределах одного
UID; это заявлено явно, а не маскируется под OS-аутентификацию.

Этот change заменяет дизайн отменённого `allow-single-operator-review-extension`
(OS-broker, абсолютный предел три), который не реализован и в дереве отсутствует.

## Acceptance
### Requirement: Однократное операторское разрешение при исчерпанном остатке
#### Scenario: Preview и authorize
- [C1] Preview точного остановленного run возвращает digest и не создаёт слот. `--authorize` с текущим digest добавляет ровно одну неизменяемую запись вне старых runs; устаревший или подменённый digest отклоняется без записи. Профиль `max_review_cycles` остаётся строго 2.

### Requirement: Кооперативная граница и устойчивость к повтору
#### Scenario: Worker, гонка, повтор
- [C2] Вызов из worker-контекста отклоняется до появления слота. Гонка двух операторов, повтор подтверждения и потерянный ответ дают не более одного слота. Старые runs, verdicts, receipts, evidence и accounting сохраняются побайтно.

### Requirement: Привязка слота к поддерживаемому recovery
#### Scenario: Единственный successor
- [C3] Ссылка на разрешение записывается в первоначальный recovery context до dispatch; повторный или частичный claim не создаёт второго child. Provisional и final продолжение делят один lineage ordinal и один слот.

### Requirement: Слот не ослабляет гейты
#### Scenario: Финальные проверки и история
- [C4] Со слотом сохраняются свежие proofs, handoff, sync/archive, final verification и publication floor. Retained read-only история не получает ни исполнения, ни слота; установка runtime сама по себе слот не выдаёт.

## Scope
- `scripts/changerail/review_allowance.py`, `local_delivery.py`, `native_workflow.py`: единый расчёт allowance, двухфазный CLI, интеграция doctor/recovery/review/status.
- `tools/changerail/tests/test_review_allowance.py`, `test_review_allowance_integration.py`, `test_review_allowance_recovery.py`, `test_native_execution_contract.py`: адресные регрессии C1–C4.
- `openspec/specs/native-delivery/spec.md`, `openspec/config.yaml`, `tools/changerail/README.md`, `docs/operations.md`, навыки deliver/review, комментарий профиля: приведение контракта к фактическому поведению.
- `openspec/changes/allow-single-operator-review-extension/` и карточка `5.canceled`: архивирование истории и исправление недостоверного `Result`.

## Non-Goals
- OS-аутентификация оператора, broker, раздельные UID, внешний ledger.
- Абсолютный предел три review, unlimited через профиль, накопление слотов.
- Автоматический retry, новая карточка как способ обнулить accounting.
- Изменение принятого Acceptance/Scope под видом repair.
- Продуктовые исправления конкретного потребителя и его retained-данные.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `add-operator-review-allowance`

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Design
- Реализация принадлежит `design.md`: кооперативная граница, двухфазный digest, неизменяемые записи вне runs, единый расчёт остатка, привязка к единственному successor.
- Evidence seams: preview без побочных эффектов, отказ worker-контекста, гонка и повтор authorize, частичный claim, сохранение финальных гейтов и read-only истории.
- Runtime-safety: записи под блокировкой проекта, append-only и atomic write, отрицательный остаток как ошибка, отсутствие второго writer/child.
- `CHRL_ENGINE_USE_FD` — shared-use lease обычного release launcher, а не worker-полномочие; его исключение из признаков worker-контекста обязательно для штатного вызова через выбранный `.changerail/chrl`.

## Delivery Budget
- primary_invariant: одно явное операторское разрешение даёт ровно один дополнительный слот review при исчерпанном остатке, не меняя историю, обычный лимит двух автономных review и финальные гейты
- expected_wall_minutes: 180
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 6
- estimated_production_loc: 520

## Verify
- Планируемые проверки; реализация уже существует и подтверждена прогоном 120 passed. Точные команды и observations сохраняются при передаче в review.
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "preview and append-only authorize", "precondition": "Терминальный остановленный run с исчерпанным остатком", "action": "Выполнить preview, затем authorize с текущим и устаревшим digest; проверить профиль и остаток", "expected": "Preview не создаёт слот; authorize добавляет ровно одну запись; устаревший digest отклоняется; max_review_cycles остаётся 2", "method": {"kind": "test", "target": "tools/changerail/tests/test_review_allowance.py"}, "stage": "implementation"},
    {"condition": "C2", "seam": "cooperative boundary and idempotence", "precondition": "Синтетический run и два конкурирующих оператора", "action": "Вызвать из worker-контекста, повторить authorize, смоделировать потерянный ответ и гонку", "expected": "Не более одного слота; worker отклонён; история и accounting побайтно сохранены", "method": {"kind": "test", "target": "tools/changerail/tests/test_review_allowance_integration.py"}, "stage": "implementation"},
    {"condition": "C3", "seam": "single successor binding", "precondition": "Выданный слот и поддерживаемый recovery", "action": "Провести слот, прервать между claim/dispatch, повторить; проверить provisional и final", "expected": "Один child; повторный слот не выдаётся; provisional и final делят один ordinal и слот", "method": {"kind": "test", "target": "tools/changerail/tests/test_review_allowance_recovery.py"}, "stage": "implementation"},
    {"condition": "C4", "seam": "gates and read-only history", "precondition": "Слот выдан; исторический retained read-only run", "action": "Пройти failed floor, handoff и publication проверки; запросить статус и исполнение исторического run", "expected": "Финальные гейты обязательны; read-only история не получает ни исполнения, ни слота", "method": {"kind": "test", "target": "tools/changerail/tests/test_native_execution_contract.py"}, "stage": "final"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Отказ worker-контекста, digest-привязка к проверенному запросу, точная проверка проекта, ancestry, frozen identity и начального payload", "conditions": ["C1", "C2", "C3"]},
    {"kinds": ["mutation", "restart", "concurrency"], "applies": true, "decision": "Append-only записи вне старых runs под блокировкой проекта, atomic write, единственный successor, отказ при неоднозначном или частичном claim", "conditions": ["C2", "C3"]},
    {"kinds": ["publication"], "applies": true, "decision": "Слот даёт только бюджет review; commit, push, archive и publication floors остаются обязательными и отдельными", "conditions": ["C4"]},
    {"kinds": ["external_effects"], "applies": false, "decision": "Локальные синтетические проекты и git fixtures; реальные доставки, сеть и провайдеры не используются", "conditions": []}
  ]
}
```
- `./bin/test-changerail`
- `./.venv/bin/python -m ruff check scripts tools/changerail/tests distribution.py`
- `git diff --check`
- `./.changerail/openspec validate add-operator-review-allowance --strict --no-interactive`

## Related
- `openspec/changes/add-operator-review-allowance/proposal.md`
- `openspec/changes/add-operator-review-allowance/design.md`
- `openspec/changes/add-operator-review-allowance/specs/native-delivery/spec.md`
- `openspec/changes/add-operator-review-allowance/tasks.md`
- `openspec/changes/archive/2026-09-12-allow-single-operator-review-extension/` — отменённый предшественник, сохранён как история
- `scripts/changerail/review_allowance.py`, `scripts/changerail/local_delivery.py`
- `.runtime/planning/repo-cleanup/UNPUBLISHED-WORK-ASSESSMENT.md` — разбор и результаты прогона

## Result
Реализация существует в dev-checkout и подтверждена прогоном 120 passed
(`test_review_allowance*` + `test_release_transaction_size` +
`test_native_execution_contract`).

Оформление выполнено 2026-09-12: созданы change `add-operator-review-allowance`
и эта карточка; `openspec/config.yaml` и публикуемый `tools/changerail/README.md`
приведены к фактическому контракту; отменённый change архивирован, а недостоверный
`Result` его карточки исправлен. Каноническая спека обновляется delta-спекой
этого change при архивации.

Admission ещё не выполнен: `native-accept`, независимый review и финальные
гейты впереди.

## Next
- Выполнить structural admission (`native-accept`) после остановки других активных доставок.
- Передать свежие proofs внешнему независимому review и пройти обычные финальные гейты.
- При архивации применить delta-спеку к канонической `native-delivery`.

## Log
- 2026-09-12T15:00:00Z карточка создана по итогам разбора неопубликованной работы; кода не менялось, admission не выполнялся.
- 2026-09-12T16:00:00Z оформление: change и карточка созданы, `openspec/config.yaml` и `tools/changerail/README.md` синхронизированы, отменённый change архивирован, его `Result` исправлен, change `close-exhausted-native-delivery` пересобран под семантику allowance. Оба change и канонические спеки валидны; Ruff, публичный скан и `git diff --check` чисты.
