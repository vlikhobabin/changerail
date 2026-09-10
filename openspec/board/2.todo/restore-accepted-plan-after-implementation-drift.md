# Восстановить принятый план после случайной правки карточки исполнителем

## Status
2.todo

## Lifecycle
openspec-v1

## Owner
ChangeRail

## Priority
P1

## OpenSpec Stage
native artifacts prepared; recovery gates reproduced; not admitted

## Source
- Поручение оператора от 2026-09-10: создать карточку в ChangeRail по остановке OSS-FIX-04A потребителя qa-mcp.
- Потребитель: qa-mcp, baseline `a3774e89cb19c88e547be5d532012fe998aea43d`, установленный runtime `2.0.0-candidate.5`.
- Исходный run: `20260910T065103Z-oss-fix-04a-isolate-display-and-host-agent-settings`.
- Первая неудачная попытка обычного resume: `20260910T071820Z-oss-fix-04a-isolate-display-and-host-agent-settings`.
- Исходник ChangeRail при подготовке карточки: `2e0a164`. Его текущий shared-source runtime-repair имеет другую границу применимости; дефект необходимо воспроизвести на актуальном исходнике перед реализацией.

## Summary
Исполнитель случайно изменил замороженный раздел `Next` принятой карточки при
финальном обновлении её состояния. Scope, Acceptance и нормализованные OpenSpec
артефакты не изменились. Runner правильно отказался считать изменённый контракт
принятым, но штатный recovery не даёт вернуть точные исходные байты:
неисправленный payload проходит проверку сохранённого manifest и не проходит
проверку плана; возврат `Next` восстанавливает hash плана, но нарушает
совпадение payload с manifest. Оба отказа воспроизведены отдельно на текущем core.

Нужен явный, проверяемый переход восстановления точных байтов принятого плана
для остановленного run с уже завершёнными checkpoint/evidence. Он должен
сохранить историю и счётчики, записать основание и diff отдельной квитанцией,
обновить необходимые доказательства и вернуть управление штатному runner.
Это восстановление прежнего решения, а не принятие нового scope.

## Reproduction And Observed State
1. Принять одну native-карточку с `Next` и одним change, запустить доставку.
2. Завершить task groups и записать focused evidence. В последней сессии
   изменить `Result`, `Log` и `Next`, не меняя acceptance или текст задач.
3. Проверка после сессии возвращает exit 2:
   `accepted native OpenSpec plan changed; explicit replan required`.
4. Вызвать обычный `resume` точного run. В наблюдаемом случае doctor подтвердил
   exact recovery payload, затем импорт принятого плана вернул ту же ошибку
   до запуска исправляющей сессии. Попытка resume тоже сохранена.
5. При первоначальном разборе сравнение в памяти показало: возврат исходного
   `Next` восстанавливает hash контракта. Последующий локальный workaround
   и синтетическое воспроизведение описаны отдельно ниже.

Наблюдения qa-mcp на момент первых двух остановок:

- Три группы записаны complete; успешного общего handoff/finalize нет.
- 114 focused offline-тестов: 0 failures/errors, итоговый JUnit 20.935 s.
- Отдельный stdio integration: 1 тест, 0 failures/errors, 3.338 s.
- Compile и scoped/canonical OpenSpec validation прошли. Эти проверки не
  заменяют отсутствующие final floor, независимое review и публикацию.
- Review cycles: 0 из 2; archive и publication не начинались; live runtime не запускался.
- Принятый card contract SHA-256:
  `577ef3c1ca334eadef881a08441fc72225b9314cac49841a8335f0be93982f24`.
- После изменения `Next`:
  `77ea7ead2190934a6213da0796052a0ad048289381b4506382dfef32683d669d`.
- Восстановление только `Next` в памяти даёт исходный hash; все нормализованные
  OpenSpec artifact hashes совпадают с принятым планом.

## Уточнение инцидента и воспроизведение (2026-09-10)

Read-only проверка подтвердила последующий локальный операторский workaround:
возвращён Next, в failed child добавлен native-plan из первого run, его manifest
пересэмплирован установленным CLI. Исходный run сохранён; manifest child изменён,
а before-копия удерживается отдельно. Это не append-only переход по C2 и не
образец реализации общего инструмента. Установка осталась candidate.5.

Третий run `20260910T073430Z-oss-fix-04a-isolate-display-and-host-agent-settings`
завершился `2026-09-10T07:38:13Z`, exit 2, с причиной
`implementation session exited without a handoff`. Созданы native-sync receipt
и mapping report. Handoff отклонён из-за отдельной dangling ссылки FIX-03 на
отсутствующую todo-карточку FIX-02. Review cycles всё ещё 0; успешной доставки нет.
Эта ошибка целостности доски не входит в восстановление Next и не должна обходиться.

На текущем ChangeRail `6167dc5` выполнен generic harness с настоящими pinned
OpenSpec 1.3.1, admission, native start и production gates без подмены этих gates.
12 проверок прошли: modified Next допускается exact payload, но отклоняется
require_plan/import_accepted; исходный Next допускается plan, но отклоняется
recovery_source (`previous delivery manifest lacks exact fingerprint proof`).
Failed import оставляет child без native-plan; исходная история не изменилась.

Граница доказательства: остановка и child созданы harness; публичные doctor/resume,
модельные сессии, checkpoint, review и observed evidence не запускались. Это
воспроизведение двух gates, а не end-to-end доказательство C1–C4. В реализации
нужны дополнительные fixture и регрессии из tasks.md. Локальный отчёт:
`.runtime/plan-restoration-exploration/result-20260910b/report.json`; не публикуется
и не является обязательной зависимостью clean-clone тестов.

## Acceptance
- [C1] На синтетическом stopped native run с завершёнными checkpoint и evidence команда подготовки показывает точный drift относительно достоверного принятого источника; применение явно одобренного восстановления возвращает только исходные байты изменённого `Next`. Произвольный новый текст, подмена исходника, изменение Scope/Acceptance, артефактов, профиля или продуктового кода этим разрешением не принимаются; отказ происходит до записи.
- [C2] Восстановление создаёт отдельную квитанцию с target/run, основанием и полномочием, принятым hash, before/after hashes, точным diff и связью с исходным run и неудачным resume. Старые run.json, manifests, receipts, evidence, времена, попытки и review accounting остаются побайтно неизменными. Dry-run не меняет payload; живой writer, drift после подготовки, повторное применение и прерывание обрабатываются явно, без двойного применения и перезаписи истории.
- [C3] После восстановления штатный runner признаёт новый переход, определяет устаревшие proof/fingerprints и получает свежие необходимые evidence до продвижения. Сохраняет завершённые задачи только при доказанной неизменности их содержания; незавершённые finalize, sync, review, archive, final floor и publication не пропускаются. Лимит двух независимых review общий с предшественниками; контроль с уже потраченным review и исчерпанным остатком не создаёт дополнительной попытки.
- [C4] Документирован и проверен путь применимости к исходному классу инцидента: установленная локальная runtime-копия, завершённые checkpoint/evidence и последующая неудачная recovery-попытка. Простая установка новой версии или исключение `Next` из hash не объявляются достаточным восстановлением. Если нужен переход execution identity, он имеет отдельные точные проверки совместимости и полномочий без изменения исторических runs. В синтетическом end-to-end сценарии доказана доступность продолжения; реальный qa-mcp run остаётся отдельным операторским действием.

## Scope
- `scripts/changerail/openspec_context.py`: идентичность принятого плана и диагностика drift.
- `scripts/changerail/local_delivery.py`, `scripts/changerail/native_workflow.py`, `scripts/changerail/openspec_board.py`: точный predecessor, переход восстановления, invalidation/refresh evidence и возврат к runner.
- Новый ограниченный модуль/schema квитанции при необходимости; `scripts/changerail/runtime_repair.py` — только для явного разграничения двух механизмов и проверки совместимости.
- `tools/changerail/skills/chrl-native-deliver/SKILL.md`: явно перечислить допустимые изменения состояния карточки и запрет правки замороженного `Next`; сообщения completion/handoff должны соответствовать реальному результату команды.
- Адресные регрессии в `tools/changerail/tests/test_openspec_recovery_boundaries.py`, `test_native_openspec_integration.py`, `test_native_execution_contract.py` и затронутых тестах evidence/repair.
- `distribution.py` и installation transition tests: точная смена установленного runtime без снятия read-only policy и без изменения истории.
- `docs/operations.md`, `docs/runtime-repair.md`, при необходимости отдельный runbook; capability `native-delivery`.

## Non-Goals
- Не исправлять продуктовый код qa-mcp и не продолжать его остановленный run в рамках этой карточки.
- Не принимать новый scope/acceptance под видом восстановления; не отключать проверку плана/payload и не исключать `Next` из hash как обход для старого run.
- Не редактировать старые manifests/receipts вручную; не создавать новый независимый delivery поверх старого payload и не обнулять review/evidence accounting.
- Не возобновлять оператором остановленные или исторические runs по одному факту установки нового runtime.
- Не выполнять live 1С, deployment, release tag или публикацию потребителя. Оператор 2026-09-10 разрешил реализацию, commit, push и новый release tag; это не разрешает изменение данных или запуск доставки потребителя.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `restore-accepted-plan-after-implementation-drift`

## Design
- Доказательства строятся на временном generic-проекте с настоящими gates и контролируемыми сессиями; потребительские runtime-логи не нужны для clean-clone регрессии.
- План реализации: `openspec/changes/restore-accepted-plan-after-implementation-drift/design.md`; prepare/apply с отдельным effective manifest, подтверждённым ancestry origin и явным installed runtime transition.
- Основной риск — незаметно принять новый контракт или подменить доказательство. Сравнивать достоверный принятый источник, текущий payload и разрешённый точный diff; никакого принятия по сходству текста.
- Восстановление меняет карточку/effective payload и влияет на последующую публикацию. Нужны append-only lineage, блокировка одного writer, отрицательные контроли и доказательство обновления evidence до продвижения.
- Raw evidence, профили и session/auth state остаются в ignored каталоге потребителя. В Git допускаются только синтетические fixtures и обезличенное описание.

## Delivery Budget
- primary_invariant: Точное восстановление принятого плана возвращает остановленный run к штатной доставке, сохраняя историю и обязательность актуальных доказательств.
- expected_wall_minutes: 180
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 10
- estimated_production_loc: 1000


## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Verify
План доказательства C1–C4 при реализации; результаты ограниченного воспроизведения приведены выше:

- Перенести воспроизведение в регрессию и расширить completed/evidence fixture: drift плана на точном сохранённом payload и несовпадение manifest после ручного возврата `Next` в одноразовой fixture.
- Адресно выполнить изменённые recovery/native integration/execution identity тесты; добавить позитивный путь восстановления и отрицательные C1–C4 контроли.
- Сравнить hashes всей исходной истории до/после; проверить fresh evidence, порядок продолжения и общий остаток review, включая неудачную resume-попытку.
- `git diff --check`; strict validation нового change и затронутой canonical spec при реализации. Создание карточки не требует запуска тестов runtime.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "accepted plan to restoration proposal", "precondition": "Stopped fixture with completed groups and only Next drift", "action": "Prepare and apply exact restoration plus hostile edits", "expected": "Only accepted Next bytes are restored; foreign changes fail before writes", "method": {"kind": "test", "target": "tools/changerail/tests/test_openspec_recovery_boundaries.py"}, "stage": "implementation"},
    {"condition": "C2", "seam": "restoration receipt and project lock", "precondition": "Original and failed recovery histories retained", "action": "Apply, repeat, interrupt and race with a writer; compare history hashes", "expected": "Append-only transition preserves all history and rejects stale or competing writes", "method": {"kind": "test", "target": "tools/changerail/tests/test_openspec_recovery_boundaries.py"}, "stage": "implementation"},
    {"condition": "C3", "seam": "restored payload to runner continuation", "precondition": "Restoration invalidates prior payload evidence and retains review usage", "action": "Resume with stale/fresh evidence and remaining/exhausted review allowance", "expected": "Fresh required proof gates all later stages; previous attempts remain counted", "method": {"kind": "test", "target": "tools/changerail/tests/test_native_openspec_integration.py"}, "stage": "implementation"},
    {"condition": "C4", "seam": "installed predecessor compatibility", "precondition": "Synthetic installed-copy predecessor matches the documented incident class", "action": "Exercise supported compatibility transition and incompatible controls", "expected": "An explicit verified route reaches continuation; installation alone never grants recovery", "method": {"kind": "test", "target": "tools/changerail/tests/test_native_execution_contract.py"}, "stage": "implementation"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Authenticate accepted bytes, run identity and exact authorized diff before writes", "conditions": ["C1", "C4"]},
    {"kinds": ["mutation", "restart", "concurrency"], "applies": true, "decision": "Project lock, append-only transition and interrupted/repeated application controls preserve ownership and history", "conditions": ["C2", "C3"]},
    {"kinds": ["publication"], "applies": true, "decision": "Recovery affects delivery authority; require fresh proof and normal review/final/publication gates in disposable fixtures", "conditions": ["C3", "C4"]},
    {"kinds": ["external_effects"], "applies": false, "decision": "This implementation is verified in temporary local projects without real consumer delivery or network publication", "conditions": []}
  ]
}
```

## Related
- `docs/operations.md`
- `docs/runtime-repair.md`
- Optional local-only evidence in the qa-mcp checkout: `.runtime/qa-roadmap/oss-00/fix-04a-start/blocker.json`, `blocker.md`, `proposed-next-restoration.patch`, `runner.log`, `resume-01.log`. Эти файлы не копировать в ChangeRail и не делать обязательными входами тестов.

## Result
accepted native OpenSpec plan; structural admission only

## Next
- Реализовать принятый план в основном checkout ChangeRail, проверить C1–C4, выполнить независимое ревью и выпустить новый RC по docs/releasing.md. Реальные consumer runs остаются отдельным действием.

## Log
- 2026-09-10 Карточка создана по поручению оператора на основании сохранённых результатов FIX-04A и сравнения с текущей границей runtime-repair. Посторонняя правка `docs/migration.md` сохранена.
- 2026-09-10 Уточнён результат локального workaround и третьего run; воспроизведены два gates и missing-plan child на текущем core; подготовлен один native change без admission.
- 2026-09-10 Оператор разрешил довести change до завершения и публикации нового релиза; обратимые исправления выполнять без дополнительных остановок.
- 2026-09-10T10:36:38Z accepted native OpenSpec plan
