# Завершить неуспешную native-доставку после исчерпания review

## Status
2.todo

## Lifecycle
openspec-v1

## OpenSpec Stage
artifacts

## Owner
unassigned

## Source
- Разбор terminal native delivery после исчерпания allowance (два автономных NO-GO), 2026-09-11.

## Summary
После исчерпания allowance runner останавливает доставку, но оставляет карточку в
3.inprogress. Исчерпание наступает и после двух автономных NO-GO, и после
терминального NO-GO при использованных операторских слотах. Команды явного
завершения неуспешной попытки нет;
single-active-card блокирует следующий принятый план. Нужен узкий переход
закрытия с сохранением истории, отдельный от technical model recovery.

## Acceptance
- [C1] Для точного остановленного native run с исчерпанным allowance (`remaining = 0`) и последним NO-GO можно подготовить результат закрытия: карточка, run, расход review, выданные слоты, verdict, сохранённый текущий payload и причина завершения. Применение по явному операторскому поручению переводит карточку в 5.canceled с результатом «доставка неуспешна». Закрытие не создаёт GO, review, commit или push, не выдаёт и не возвращает review-слоты и не объявляет OpenSpec change успешно доставленным.
- [C2] Старые runs, receipts, manifests, verdicts и evidence сохраняются побайтно; закрытие фиксируется отдельной записью. Payload после последнего review сохраняется отдельно как непроверенный. Повтор не создаёт второй переход. Живой writer, чужой run, изменившийся после подготовки payload и граница публикации отклоняются до изменения доски.
- [C3] Закрытая карточка освобождает активное место на доске и не может продолжаться через обычный resume. Новая связанная карточка допускается как план перепроектирования; закрытие не принимает её, не запускает и не обнуляет accounting исходной доставки. Инструкция разделяет закрытие старой попытки и отдельное принятие нового плана.
- [C4] Проверенный новый комплект может закрыть доказанную native историю installed 2.0.0-rc.3 через явный --project без замены installed runtime, lock, launcher или profile. Отдельная terminal-only совместимость не расширяет права resume/restoration; неизвестные или подменённые provenance отклоняются.

## Scope
- `scripts/changerail/native_closure.py`, native CLI/execution/status/board hooks в `scripts/changerail/`: proposal, snapshot, закрытие и terminal-only rc.3 compatibility.
- `tools/changerail/tests/test_native_closure.py`, `test_native_closure_installed.py` и затронутые execution contract tests: synthetic regressions.
- `docs/operations.md` и distribution inventory при необходимости: поставка модуля и операторская инструкция.

## Non-Goals
- Выдача, возврат, переиспользование или обнуление review-слотов; повышение автономного лимита; автоматический retry.
- Универсальная система recovery и изменение действующего technical recovery.
- Автоматическое принятие/запуск карточки-преемника.
- Переписывание frozen плана, старой истории или installed runtime потребителя.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `close-exhausted-native-delivery`

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Design
- Реализация принадлежит связанному design.md; proof seams — exhausted ancestry, round-trip snapshot, terminal execution guards и внешний copy-install CLI.
- Existing project lock, digest-bound proposal и отдельный append-only intent/completion; frozen history сохраняется, неполный intent блокирует writer.
- После закрытия dirty payload остаётся сохранённым; подготовка чистой базы и новый план выполняются отдельно, без автоматической публикации ремонта.

## Delivery Budget
- primary_invariant: explicit terminal closure frees an exhausted delivery without changing history or granting execution authority
- expected_wall_minutes: 120
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 10
- estimated_production_loc: 750

## Verify
Планируемые проверки, ещё не выполненное evidence; exact commands и observations
сохраняются по процедуре verification/scenarios.md.
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"explicit exhausted closure","precondition":"Stopped synthetic ancestry with exhausted allowance (remaining = 0) and last NO-GO","action":"Prepare and explicitly apply closure; exercise invalid states","expected":"Card is canceled as unsuccessful; no review/archive/commit/push starts; slots and usage are not returned or reset","method":{"kind":"inspection","target":"openspec/changes/close-exhausted-native-delivery/verification/scenarios.md"},"stage":"implementation"},
    {"condition":"C2","seam":"restorable payload and immutable history","precondition":"Current unreviewed payload differs from retained review and includes new/deleted/mode/symlink paths","action":"Round-trip snapshot, apply, interrupt and repeat with stale/conflicting variants","expected":"History bytes and review usage are unchanged; one transition; conflicts preserve user edits","method":{"kind":"inspection","target":"openspec/changes/close-exhausted-native-delivery/verification/scenarios.md"},"stage":"implementation"},
    {"condition":"C3","seam":"terminal lineage and board availability","precondition":"Completed closure or interrupted closure intent","action":"Exercise execution/recovery routes and board checks; create linked backlog plan","expected":"Closed ancestry cannot execute; completed closure frees board; new plan is not auto-accepted","method":{"kind":"inspection","target":"openspec/changes/close-exhausted-native-delivery/verification/scenarios.md"},"stage":"implementation"},
    {"condition":"C4","seam":"installed rc3 terminal compatibility","precondition":"Synthetic rc3 copy-install project and separate reviewed candidate tool","action":"Run external CLI --project closure plus provenance and resume negative cases","expected":"Only supported history closes; installed runtime/config/history unchanged; no execution authority added","method":{"kind":"inspection","target":"openspec/changes/close-exhausted-native-delivery/verification/scenarios.md"},"stage":"final"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"Exact project/lineage/HEAD/provenance checks; digest binding and worker-role rejection","conditions":["C1","C2","C4"]},
    {"kinds":["mutation","concurrency"],"applies":true,"decision":"Project lock, no-writer checks, restorable snapshot, append-only intent and idempotent conflict-safe repeat","conditions":["C1","C2","C3"]},
    {"kinds":["publication"],"applies":true,"decision":"Reject publication boundaries and all execution routes of closed lineage; closure never calls commit/push","conditions":["C1","C3","C4"]},
    {"kinds":["restart","external_effects"],"applies":false,"decision":"Synthetic local CLI/projects only; no services, network publication or provider runtime changes","conditions":[]}
  ]
}
```
- `./bin/openspec validate close-exhausted-native-delivery --strict --no-interactive`
- Focused pytest, Ruff и diff-check: команды в verification/scenarios.md.

## Related
- `openspec/changes/close-exhausted-native-delivery/proposal.md`
- `openspec/changes/close-exhausted-native-delivery/design.md`
- `openspec/changes/close-exhausted-native-delivery/specs/native-delivery/spec.md`
- `openspec/changes/close-exhausted-native-delivery/tasks.md`
- `openspec/changes/close-exhausted-native-delivery/verification/scenarios.md`

## Result
Принят native OpenSpec plan; structural admission READY. Реализация не начата.
Doctor 2026-09-11: clean-start и single-active-card не пройдены — остаётся
активная recover-after-technical-model-failure и отдельный dirty payload
self-host engine/recovery. Сначала завершить эту работу, затем подготовить
scoped plan commit и повторить doctor перед outer run. Проверка remote
в диагностике пропущена через --no-remote; готовность публикации не проверена.

## Next
После native acceptance и подготовки scoped plan commit выполнить doctor.
Запускать outer run только при отсутствии другой активной доставки и
постороннего dirty payload. Реализация обновляет tasks/Result/Log, сохраняет
frozen план и передаёт свежие proofs внешнему независимому review.

## Log
- 2026-09-11: создан отдельный backlog proposal; существующая работа над recovery сохранена.
- 2026-09-11: подготовлены proposal/design/specs/tasks и четыре сценария evidence; explicit rc.3 terminal compatibility включена до принятия плана.
- 2026-09-11T07:01:21Z accepted native OpenSpec plan
