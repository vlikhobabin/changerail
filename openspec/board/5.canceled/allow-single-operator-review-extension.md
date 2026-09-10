# Одноразовое операторское разрешение дополнительного исправления и review

## Status
5.canceled

## Lifecycle
openspec-v1

## OpenSpec Stage
canceled

## Owner
unassigned

## Priority
P1

## Source
- Поручение оператора от 2026-09-10: оформить обсуждённое ограниченное исключение из лимита review отдельной карточкой ChangeRail.
- Инцидент потребителя qa-mcp: OSS-FIX-04A `oss-fix-04a-isolate-display-and-host-agent-settings`, два последовательных NO-GO после реализации и repair.
- Связанное восстановление принятого `Next` уже доставлено отдельно: `openspec/board/4.done/restore-accepted-plan-after-implementation-drift.md`. Оно не добавляет review allowance.

## Summary
После второго NO-GO runner правильно останавливает доставку, но сейчас не имеет
поддерживаемого способа принять отдельное ограниченное решение оператора о ещё
одном исправлении. В FIX-04A второй review обнаружил, что публичное поле `error`
всё ещё пропускает недоверенный текст ответа host-agent. C1/C2/C4 были приняты,
после repair прошли 117 тестов, однако GO, завершения и публикации нет. Остаток
работы определён: локальный allowlist кодов ошибок с постоянным безопасным
fallback, регрессии затронутых путей HTTP/JSON и актуализация evidence R2/R3.
Успешные тесты не закрывают finding R1 и не заменяют независимый verdict.

Нужен один явный операторский допуск на один дополнительный repair и review
после двух обычных циклов. Абсолютный предел — три независимых review на всю
историю одной доставки, включая предшественников и recovery. Исключение нельзя
выдать повторно, получить переименованием карточки или автоматически заменить
новой карточкой. Неудача третьего review заканчивает попытку терминальным
`exhausted`; дальнейшее перепроектирование требует отдельного решения оператора
с сохранением связи с неудачной доставкой и не является автоматическим retry.

Текущий код считает завершённые verdict и наследованный расход в
`review_budget_usage()` и отдельно проверяет `>= 2` при запуске review, после
NO-GO и после failed final verification. Настройка `max_review_cycles` принимает
только 2. Следует сохранить обычное правило и ввести единый расчёт разрешённого
перехода по сохранённой истории и валидной квитанции, вместо общего повышения
настройки или разрозненных обходов gates.

## Acceptance
- [C1] После двух обычных review с последним валидным NO-GO runner остаётся остановлен и может подготовить конкретное предложение: findings, причина неполного предыдущего repair, неизменные Acceptance, ограниченный diff scope, план регрессий/evidence и исход следующей неудачи. Только явное решение доверенного оператора разрешает один дополнительный repair и review №3. Worker может подготовить предложение, но его файл или `approved: true` не являются полномочием. Отсутствующее, чужое, устаревшее или расширяющее scope разрешение отклоняется до запуска writer; разрешение review не предоставляет commit/push или runtime authority.
- [C2] Разрешение записывается отдельной неизменяемой квитанцией, связанной с project identity, корневой delivery lineage, точным predecessor, payload, последним NO-GO и планом repair; сохраняет оператора, основание и объём `one repair + one review`. Старые run.json, manifests, receipts, verdicts, evidence, времена и попытки побайтно сохраняются. Дополнительная попытка атомарно резервируется при запуске; повторное применение, конкурирующий resume, падение после резервирования, перенос между проектами и подмена fingerprint не создают второго права. Единственный расчёт allowance применяется к review, semantic repair, failed-floor repair, recovery и installed transition; суммарный предел 3 не сбрасывается новым child run, именем карточки или установкой runtime.
- [C3] Перед review №3 handoff содержит для каждого разрешённого finding воспроизведение, причину, исправление всего затронутого пути, регрессии и актуальное evidence. GO №3 допускает только обычные archive/final verification/publication gates с актуальными fingerprint. NO-GO №3 или необходимость нового существенного repair после него приводят к терминальному `exhausted`, без нового предложения исключения, синтетического GO, сброса счётчиков или автоматической replacement-карточки. Оператор может приостановить или отменить работу до следующего перехода; `paused` не продвигается автоматически, `canceled` и `exhausted` терминальны. Resume после pause сохраняет то же разрешение и остаток; штатное обновление evidence после archive не превращается в скрытый новый цикл исправления.
- [C4] Технический сбой не классифицируется как NO-GO и не создаёт бесконечных повторов: число автоматических восстановлений ограничено явной конечной политикой, continuation сохраняет ID и резервирование исходного attempt, повторные сбои дают `infrastructure-blocked` без автоматического перезапуска. Документированы статусы, pause/cancel, границы доверенного операторского подтверждения и точный путь совместимости для остановленных installed runs с двумя сохранёнными NO-GO. В синтетическом end-to-end доказаны разрешённое продолжение и остановки при отказах; установка новой версии, восстановление плана и runtime-repair сами по себе не предоставляют исключение. Реальные consumer run, продуктовый fix и публикация остаются отдельными операторскими действиями.

## Scope
- `scripts/changerail/local_delivery.py`: единая политика allowance, наследование/reservation, review/repair/final-floor/recovery transitions и диагностируемые конечные состояния.
- `scripts/changerail/native_workflow.py`, `scripts/changerail/runtime_repair.py` и механизм восстановления плана: интеграция через общую политику без пополнения allowance; точная совместимость остановленных installed predecessors.
- `scripts/changerail/review_allowance.py`, ограниченные authority broker/client и schema в `tools/changerail/schemas/`: единая политика, prepare/apply/resume и operator approve/pause/unpause/cancel через защищённые Linux principals.
- Host execution boundary и затронутый Codex adapter: worker не владеет coordinator/broker, same-UID bypass не разрешает исключение; protected host launcher не заменяет проектные launcher/profile bytes.
- `distribution.py`, `distribution.json`, новый broker entrypoint и CI: доставка компонентов без host config/ledger/credentials и отдельный реальный Linux multi-UID test.
- `tools/changerail/tests/test_local_changerail_delivery.py`, `test_native_openspec_integration.py`, `test_openspec_recovery_boundaries.py`, `test_native_execution_contract.py` и `test_runtime_repair.py`: адресные синтетические регрессии для C1–C4.
- `openspec/specs/native-delivery/spec.md`, `AGENTS.md`, `openspec/config.yaml`, README/DISTRIBUTION, `docs/operations.md`, `docs/runtime-repair.md`, затронутые runner/worker skills и сообщения CLI: обычный лимит 2, единственное операторское исключение +1 и абсолютный предел 3.

## Non-Goals
- Не исправлять qa-mcp и не возобновлять его run в рамках этой карточки; описание FIX-04A — мотивация, не разрешение на consumer delivery.
- Не увеличивать обычный лимит через профиль и не вводить неограниченный `force`, повторяемый waiver или ручное редактирование accounting.
- Не менять Acceptance под видом repair; при необходимом новом scope остановиться для отдельного решения, не выдавать новую карточку как технический способ обнулить попытки.
- Не переписывать исторические квитанции и не принимать прежний GO, успешные тесты либо операторское исключение вместо независимого review.
- Не отключать locks, frozen execution identity, актуальность evidence, runtime authorization, archive, final floor и publication gates.
- Не разрабатывать общий планировщик задач или неограниченное восстановление инфраструктуры; только конечные переходы этой доставки.
- Создание карточки не разрешает реализацию инструмента, admission, тестовый прогон, commit, push или выпуск.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `allow-single-operator-review-extension`

## Design
- Дизайн и таблица переходов: `openspec/changes/allow-single-operator-review-extension/design.md`; план подготовлен, реализация и admission ещё не выполнялись.
- Выбраны защищённый Linux authority broker, раздельные operator/coordinator/worker principals и внешний authoritative ledger; local waiver/SHA/env не дают полномочий.
- Ровно одно technical continuation на весь extension attempt; default 2, одно исключение +1 и абсолютный предел 3. Первый installed bridge покрывает точные rc.2/rc.3 payload.
- Уточнены оценки: доверенная OS-граница требует одного локального authority contour и отдельного integration proof, но не 1С runtime.
- Доверие к разрешению должно проверяться вне worker-controlled payload: описать конкретного issuer и проверяемую границу подтверждения. Один JSON в workspace не решает задачу полномочий.
- Allowance принадлежит delivery lineage, а не числу файлов verdict или текущему имени карточки. Резервирование отделяется от завершённого verdict; аварийное продолжение использует тот же attempt без возврата потраченного права в пул.
- Для infrastructure continuation определить конечный retry budget и доказательство сохранения attempt/session identity; невозможность безопасного продолжения означает остановку. Повторные ручные команды не должны обнулять этот budget автоматически.
- Независимый review остаётся обязанностью runner. Полнота repair проверяется исполнителем перед handoff и не создаёт скрытый дополнительный независимый review.
- Доказательства собираются в generic временных проектах с синтетическими секретами, реальными gates и локальным bare remote, если нужна проверка publication. Потребительские receipts, журналы и данные в Git не копировать.

## Delivery Budget
- primary_invariant: Одно доверенное операторское разрешение даёт ровно один дополнительный repair/review при сохранении истории, обязательных gates и конечного предела три review на delivery lineage.
- expected_wall_minutes: 300
- production_owners: 1
- runtime_contours: 1
- estimated_product_files: 20
- estimated_production_loc: 2000

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Verify
План проверок будущей реализации; при создании карточки runtime-тесты не запускать.

- Адресные регрессии в указанных ниже существующих test modules: default 2, единственное исключение +1, hard ceiling 3; отсутствие/подмена полномочий; immutable history; повтор, race и crash после резервирования; все repair/recovery входы; terminal/paused/infrastructure states.
- Синтетический end-to-end с installed predecessor и двумя NO-GO: явная совместимость и разрешение, один repair, fresh evidence, GO №3 и штатное завершение; отдельные отрицательные сценарии NO-GO №3 и failed final floor с необходимым новым repair.
- Перед review доказать закрытие каждого finding; после archive проверить неизменность продукта и актуальность evidence, не выдавая новый repair allowance.
- При реализации выполнить strict validation change/canonical spec и `git diff --check`; в карточке не считать этот план выполненным evidence.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "operator proposal and authority boundary", "precondition": "Stopped synthetic delivery has two retained reviews and a final NO-GO", "action": "Prepare a bounded repair proposal and exercise valid, absent, worker-issued, stale and foreign authorization", "expected": "Only explicit trusted authority enables one bounded repair and third review; other requests fail before writer launch", "method": {"kind": "test", "target": "tools/changerail/tests/test_local_changerail_delivery.py"}, "stage": "implementation"},
    {"condition": "C2", "seam": "append-only authorization and shared lineage allowance", "precondition": "Original history hashes and authorized payload are retained", "action": "Reserve, race, interrupt, repeat and resume across children; attempt fingerprint and project substitution", "expected": "History is byte-identical, reservation is single-use, all entry points retain an absolute ceiling of three reviews", "method": {"kind": "test", "target": "tools/changerail/tests/test_openspec_recovery_boundaries.py"}, "stage": "implementation"},
    {"condition": "C3", "seam": "third review through final gates and stop states", "precondition": "Authorized repair has finding-bound fresh evidence and one reserved review", "action": "Exercise third GO and NO-GO, failed final floor, archive refresh, pause, resume and cancel", "expected": "GO advances only through normal gates; new repair or third NO-GO is exhausted; pause preserves allowance and cancel is terminal", "method": {"kind": "test", "target": "tools/changerail/tests/test_native_openspec_integration.py"}, "stage": "implementation"},
    {"condition": "C4", "seam": "installed compatibility and bounded infrastructure continuation", "precondition": "Synthetic installed predecessor retains two NO-GO verdicts and an interrupted reserved attempt", "action": "Exercise explicit compatible transition, incompatible upgrade and repeated infrastructure failures", "expected": "Upgrade alone grants no exception; supported continuation retains attempt identity and finite retries end infrastructure-blocked", "method": {"kind": "test", "target": "tools/changerail/tests/test_native_execution_contract.py"}, "stage": "implementation"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Bind trusted issuer, project, lineage, predecessor, payload, verdict and exact repair scope; reject worker self-authorization and drift", "conditions": ["C1", "C2"]},
    {"kinds": ["mutation", "restart", "concurrency"], "applies": true, "decision": "Use append-only receipts, project ownership lock and atomic attempt reservation with crash/race controls and bounded continuation", "conditions": ["C2", "C3", "C4"]},
    {"kinds": ["publication"], "applies": true, "decision": "Exception only extends bounded review authority; fresh evidence, final gates and separate publication authority remain mandatory", "conditions": ["C1", "C3", "C4"]},
    {"kinds": ["external_effects"], "applies": false, "decision": "Planned proof uses temporary generic local projects and optional local bare remotes; no real consumer runtime or network publication", "conditions": []}
  ]
}
```

## Related
- `openspec/changes/allow-single-operator-review-extension/proposal.md`
- `openspec/changes/allow-single-operator-review-extension/design.md`
- `openspec/changes/allow-single-operator-review-extension/specs/native-delivery/spec.md`
- `openspec/changes/allow-single-operator-review-extension/tasks.md`
- `openspec/board/4.done/restore-accepted-plan-after-implementation-drift.md`
- `scripts/changerail/local_delivery.py`: `review_budget_usage`, `run_review`, outer delivery loop.
- `docs/operations.md`
- `docs/runtime-repair.md`
- Локальная диагностическая запись потребителя qa-mcp: `.runtime/qa-roadmap/oss-00/fix-04a-local-recovery/completion.md`. Не копировать в публичный репозиторий и не делать входом clean-clone тестов; наблюдения выше не заменяют воспроизведение в ChangeRail.

## Result
Change 1 (`reproduce-and-model`) complete: retained the ordinary two-NO-GO stop regression and its synthetic baseline observation, added closed proposal/grant/reservation/transition wire schemas plus binding validation, and retained focused pytest/wiring evidence. No operator authority, broker, reservation writer, or third-review path is implemented by this group.

Change 2 (`protect-operator-authority`) complete: added the separately configured Linux authority broker, peer-UID-separated operator/coordinator APIs, a private SQLite project/lineage/grant/reservation/event ledger, and the operator CLI entry point. The broker rejects same-UID contours, worker authority requests and unsafe host config/state paths. Focused evidence includes a mandatory dedicated CI contour that actually runs broker, operator, coordinator and worker under distinct UIDs; it proves only the trusted operator may approve the exact broker-retained proposal and that the worker cannot write ledger state.

## Next
- Use the separately planned technical-recovery change only after its implementation and verification; do not resume or rewrite this run.

## Log
- 2026-09-10 Карточка создана по поручению оператора после финального NO-GO FIX-04A; только backlog-планирование, без реализации, admission, тестов или публикации.
- 2026-09-10 По поручению «следующий шаг» подготовлены proposal/design/delta spec/tasks одного change; карточка остаётся в backlog до native admission. Уточнены trust boundary, единый reservation, terminal transitions и finite infrastructure budget. Runtime-тесты и delivery не запускались.
- 2026-09-10 Оператор поручил принять карточку и запустить полный цикл реализации через runner; разрешены подготовка, реализация, проверки и штатная публикация результата. Это не выдаёт extension grant реальному потребителю.
- 2026-09-10T14:59:29Z accepted native OpenSpec plan
- 2026-09-10T15:01:00Z started native OpenSpec delivery
- 2026-09-10 Change 1 completed: baseline remains fail-closed after two NO-GO; contracts are closed and reject duplicate IDs, negative counters, unknown authority fields, foreign bindings and scope expansion. Focused pytest and wiring receipts retained in the native run.
- 2026-09-10 Change 2 completed: retained Linux broker/ledger and real multi-UID C1 evidence; ordinary workspace records remain non-authoritative and no reservation writer or third-review delivery path has been enabled yet.

- 2026-09-10 Карточка закрыта как canceled после отказа model session на начале группы 3. Сохранённый run `.runtime/changerail/runs/20260910T150049Z-allow-single-operator-review-extension` не переписывался; публикация незавершённой реализации не выполнялась.
