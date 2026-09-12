## Context

`review_budget_usage()` считает завершённые verdict и наследованный расход.
`run_review()` и outer loop отдельно запрещают переходы при `>= 2`.
`plan_restoration.py` имеет собственную такую проверку; profile допускает только 2.
Новый child не должен превращать эти проверки в независимые бюджеты.

Существующий Codex adapter использует bypass approvals/sandbox. Поэтому
`CHRL_*`, `approved: true`, интерактивный stdin, расположение файла вне Git и
`--authorize <sha256>` не аутентифицируют человека. SHA связывает байты, а не
источник полномочий. Это ограничение определяет выбранную архитектуру.

Карточка и change относятся к инструменту. Данные инцидента потребителя служат
мотивацией; никакие реальные run, review или private evidence не нужны тестам.

## Goals / Non-Goals

**Goals:** одно дополнительное repair/review при default 2 и hard ceiling 3;
проверяемое внешнее одобрение; неизменная ancestry; единственное reservation;
конечные состояния; точный installed transition; fresh evidence и обычные gates.

**Non-Goals:** общий scheduler, облачный IAM, автоматическая выдача operator
permission, новый продуктовый fix, произвольная миграция старых runs, новый
бюджет через карточку/reinstall, запуск consumer delivery или публикация релиза.

## Decisions

### 1. Доверенная сторона находится за пределами worker

Добавить небольшой Linux authority broker, запускаемый оператором отдельно от
workspace: защищённые executable/config/state, Unix socket с `SO_PEERCRED`,
разные principal для operator, coordinator и worker. Разрешённые UID и project
registration задаются host-конфигурацией broker, а не `.changerail/profile.toml`.
Public receipts копируются в runtime проекта; authoritative ledger остаётся
у broker. JSON protocol — bounded, versioned, без shell execution и без секретов.

Operator endpoint допускает только зарегистрированный operator UID. Worker и
coordinator не могут вызывать approve/pause/unpause/cancel. Coordinator endpoint
допускает зарегистрированный runner UID только для validate/reserve/transition.
Подготовить предложение может worker; вывести его человеку — coordinator;
одобрить — отдельный операторский процесс через operator endpoint.

Исключение включается только в доверенном execution contour: coordinator и его
исполняемый runtime защищены от worker, model sessions исполняются под другим UID,
worker не имеет sudo/root/ptrace/read-write доступа к broker и coordinator.
Launcher для такого разделения задаётся защищённой host-конфигурацией, сбрасывает
полномочия до вызова проектного `bin/codex`; worker не наследует operator socket
дескрипторы, environment credentials или authority config. Профиль не может
подменить этот launcher. Установка UID/ACL/host launcher — отдельная операция
оператора; installer не делает её автоматически.

Доверенный coordinator использует защищённый interpreter/import path и не
загружает код из worker-writable `.venv`, `PYTHONPATH`, Git hooks/config или
project profile под своим principal. Модель, проверки, launcher и другие
проектные команды исполняются в worker contour; coordinator читает их результаты
как недоверенные данные. Git credential/helper hooks не исполняются с authority
правами. Загрязнение environment, import path и executable ownership входит
в отрицательные OS-boundary tests, а не компенсируется одним UID check.

Обычный текущий same-UID bypass contour продолжает работать с лимитом 2;
попытка исключения в нём получает `authority-unavailable`. В design не заявляется
защита от владельца/root хоста или от подмены доверенного coordinator. Проверка
`getuid`, наличие TTY или env flag без OS-разделения не считаются границей доверия.

Выбор: локальный broker со стандартными `socket`, `sqlite3`, `os` вместо
worker-writable waiver. Подписанный offline JSON без внешнего ledger отвергнут:
он доказывает issuer, но сам по себе не исключает rollback/replay локального расхода.
Общий authentication framework не нужен; broker обслуживает только эту lineage.

### 2. Project и lineage регистрируются один раз

`project_id` — UUID в защищённом registry с привязкой к разрешённому checkout,
canonical Git common-dir и корню файловой системы; URL remote недостаточен.
Перенос/клонирование не регистрирует новый проект автоматически. Для первого
legacy-native import operator/coordinator проверяют ancestry и фиксируют
`root_delivery_id`, root run hash, accepted change identity и список прежних
card aliases. В рамках project registry повторная регистрация той же root
или accepted change как новой lineage отклоняется.

Новый `run` для уже зарегистрированной доставки обращается к registry до writer
launch. Переименование карточки/change, новый child или копирование receipts не
выдают новую root identity. Новое перепроектирование требует отдельного решения
оператора с `supersedes` на неудачную lineage, а не автоматического retry.
Семантическое сходство произвольных новых задач автоматически не классифицируется.

### 3. Proposal и разрешение имеют точную область

Планируемый CLI runner:

```sh
./bin/chrl review-extension-prepare RUN --repair-plan PLAN.json --reason REASON --dry-run
./bin/chrl review-extension-prepare RUN --repair-plan PLAN.json --reason REASON
./bin/chrl review-extension-apply RUN --proposal PROPOSAL --grant GRANT_ID
./bin/chrl resume RUN
```

Operator-side CLI доверенного broker:

```sh
chrl-review-authority approve --project PROJECT_ID --proposal-sha256 SHA256 --reason REASON
chrl-review-authority pause --grant GRANT_ID --reason REASON
chrl-review-authority unpause --grant GRANT_ID --reason REASON
chrl-review-authority cancel --grant GRANT_ID --reason REASON
```

Названия описывают будущий API, сейчас команд нет. Approve берёт уже подготовленный
proposal из broker, показывает полный reviewable summary и требует явного
операторского вызова с точным hash. Grant не создаётся по ответу worker.

Proposal содержит project/root/predecessor IDs, HEAD, ancestry hashes, exact
payload manifest, runtime/skill/schema/profile/launcher identities, hashes двух
завершённых reviews и последнего NO-GO, accepted plan/Scope/Acceptance,
finding IDs, причину неполного прошлого repair, allowlist путей и описаний
разрешённых изменений, план регрессий/proofs и terminal outcome. Receipt хранит
broker-issued grant ID, authenticated operator principal, reason, proposal hash,
`one repair + one review`, revision ledger и при наличии target archive hash.

Eligibility: ровно два завершённых review, последний валидный NO-GO; нет
operator_interrupt, незавершённого review/verification, archive/final/publication
intent, неизвестного child, payload drift или предыдущего grant. Завершённые
failed pre-import children допустимы только при доказанной неизменной ancestry;
extension не восстанавливает Next и не расширяет plan-restoration eligibility.

Apply повторно проверяет binding под project lock и с broker. Worker-controlled
receipt считается только ссылкой: broker должен подтвердить grant и текущее
состояние. Срок пригодности определяется identity/state, а не wall-clock лимитом.
Проверка путей ограничивает механический scope; смысловое соответствие finding
проверяют handoff и независимый reviewer, а не фиктивный автоматический анализ.

### 4. Один ledger и одна функция переходов

Новый модуль `review_allowance.py` возвращает policy decision по верифицированной
ancestry и broker state: completed review IDs, reserved attempt ID, разрешённый
переход и reason отказа. `review_budget_usage` сохраняет интерфейс наблюдения;
решения больше не выводятся из количества файлов в текущем child.

Для обычных runs default остаётся 2 без обязательного broker. В зарегистрированной
extension lineage все writers сверяются с broker; его недоступность блокирует
продолжение, а не возвращает ordinary path. Дедупликация — по identity review,
не суммированию одного inherited verdict повторно. Верхняя граница:
`completed_semantic_reviews + reserved_unfinished_review <= 3`.

SQLite ledger использует транзакции и уникальные `(project_id, root_delivery_id)`
для grant и reservation. Audit events append-only, materialized current state
обновляется транзакционно. Локальные proposal, intent, applied, reservation,
continuation receipts отдельны от predecessor runs. Никакой старый файл или
состав старого run directory не меняется.

Перед первым repair writer broker атомарно выдаёт постоянный `attempt_id` и
номер review 3; обе фазы используют этот ID. `apply` авторизует переход, но не
запускает worker. `resume` резервирует attempt, создаёт durable intent, staging
полного successor и атомарно публикует его, затем подтверждает привязку у broker.
Порядок locks всегда project lock → broker transaction; broker не ждёт project
lock и не исполняет пользовательские команды.

Между broker и файловой системой нет общей транзакции. После crash reconcile
допускает только доказанные before/after states с тем же grant/attempt/intent.
Reservation никогда не возвращается в пул. Потеря local receipts, несовпадение
ledger revision или третье состояние дают отказ, а не новый attempt.
Параллельный запрос не получает второго writer lease; состояние живого
coordinator определяется peer identity и удерживаемым соединением, не одним PID
или таймером. Разрыв соединения сам по себе не доказывает смерть worker.

### 5. Переходы исключения и конечные состояния

| Состояние | Разрешённое событие | Следующее состояние и эффект |
| --- | --- | --- |
| `awaiting-operator` | explicit approve точного proposal | `authorized`, grant выдан один раз |
| `authorized` | apply + resume с целым payload | `repairing`, резервируется attempt №3 |
| `repairing` | finding-bound handoff и fresh proofs | `reviewing`, тот же attempt |
| `reviewing` | валидный GO №3 | `finalizing`, обычные archive/final gates |
| `reviewing` | валидный NO-GO №3 | `exhausted`, новых repair/review нет |
| `finalizing` | нужен новый продуктовый/семантический repair | `exhausted` |
| `finalizing` | штатный archive refresh без изменения продукта | `finalizing`, актуализация proofs |
| `finalizing` | все gates и прежняя publication authority валидны | `completed` |
| любое нетерминальное | operator pause на границе перехода | `paused`, grant/attempt сохранены |
| `paused` | explicit operator unpause + resume | прежняя стадия, те же IDs и остаток |
| любое нетерминальное | operator cancel | `canceled`, reservation не освобождается |
| execution stage | допустимый первый infrastructure failure | continuation той же стадии/attempt |
| execution stage | повторный failure либо недоказуемое continuation | `infrastructure-blocked` |

Pause/cancel записываются broker немедленно, coordinator проверяет их перед
каждым новым writer/stage. Уже выполняющаяся внешняя операция не объявляется
отменённой задним числом; сохраняются её фактические effects и безопасная точка
остановки. Отдельный operator kill остаётся `operator_interrupt` и не даёт
автоматического resume. Pause не очищает существующий infrastructure block.
`canceled`/`exhausted` терминальны для lineage; `infrastructure-blocked` не
повторяется автоматически или простым повторным CLI, требует отдельного разбора.

Конечная политика инфраструктуры: максимум **одно** автоматическое continuation
на весь extension attempt, общее для repair, review и final checks. Оно допустимо
только при завершённом старом процессе, однозначном checkpoint и возможности
продолжить прежнюю model session/check identity. Неизвестный результат launch,
частичный verdict, живой процесс, изменение fingerprint или отсутствие session
ID не дают retry — сразу `infrastructure-blocked`. Ненулевой тест/assertion
exit не инфраструктура; отсутствие GO не превращается в синтетический NO-GO.
Все входы и manual resume используют один сохранённый recovery counter.

Review №3 может иметь стандартный provisional/handoff механизм и archive
refresh, но новая независимая модельная оценка другого payload была бы review №4
и запрещена. Rerun проверки без изменения продукта разрешён только в описанных
пределах технического continuation; scope-expanding fix и новый repair запрещены.

### 6. Интеграция и installed compatibility

Переходы review/NO-GO/final-floor/resume/semantic repair используют одну policy.
Plan restoration и Python runtime-repair обращаются к ней для учёта, но сохраняют
собственные более узкие eligibility gates и не получают права выдать grant.
Нельзя после двух NO-GO сначала обычным install изменить frozen identity и затем
выдать исключение на потерянную старую связь.

Installed route выполняет новый проверенный coordinator из отдельного каталога:
`review-extension-prepare --project PROJECT --runtime-archive ARCHIVE ...`.
Apply под одним grant связывает старый exact lock, target archive, compatibility
descriptor, broker registration и projected successor identity. Обычный installer
блокируется незавершённым extension intent. Доказанный reconcile того же apply
допускается; target archive сохраняется до завершения транзакции.

Первый descriptor поддерживает точные опубликованные rc.2 и rc.3 payload,
которые проверяются по полному lock/schema/identity shape, а не строке версии.
Candidate.5/rc.1 не добавляются автоматически по аналогии с plan restoration.
Неизменные profile/launcher/project adapters обязательны; импорт в защищённый
contour не изменяет эти байты. Защищённый host execution envelope добавляется
отдельной проверенной target identity и явно входит в proposal; он не может
служить общим разрешением менять модель/продукт/план. Доказать этот bridge —
обязательное условие реализации, unsupported bridge fail closed.

Shared-source predecessor с изменившейся frozen identity этим bridge не
поддерживается; обычный новый runtime может работать с новыми runs. История
read-only, operator-stopped runs и неподдержанные стадии не становятся executable.

### 7. Доказательства и размер change

Один change сохраняет один инвариант: grant и все пути расхода не могут быть
выпущены независимо. План включает новый `review_authority.py`, клиент/ledger
и `review_allowance.py`, CLI integration, OS-boundary adapter, schemas, изменения
distribution allowlist и документации. Исходная оценка 10 файлов/1000 строк
недооценивает границу доверия: ориентир 20 файлов/2000 production LOC, 300 минут;
оценки не являются stop limits. Один production owner и один локальный authority
контур, без 1С runtime. Отдельный общий scheduler не создаётся.

| Обязательство | Регрессии и evidence при реализации |
| --- | --- |
| C1 | worker/coordinator denied approve; host config spoof; stale/foreign/broadened proposal; valid operator grant; no publication authority escalation |
| C2 | lineage rename/new child, duplicate verdict, SQLite race, crash до/после reserve и successor publication; byte hashes всех старых files/directories |
| C3 | GO/NO-GO №3, forbidden fourth review, meaningful final repair, archive refresh, pause/cancel до запуска и после stage; finding-bound fresh proofs |
| C4 | rc.2/rc.3 installed bridge, unknown payload denial, same-UID denial, missing host isolation denial, finite same-session continuation, infrastructure block |

Нужны unit/subprocess tests и generic end-to-end в temp project с local bare
remote. Отдельный Linux integration test использует разные реальные UID и
защищённый broker/coordinator: in-process mock UID не доказывает C1. Обычный CI
job использует доступные изолированные Linux test identities; отсутствие
полномочий на такой тест не записывается как pass и не заменяется worker fixture.
Тестовые identities и synthetic manifests создаются только во временной среде.
Логи — `.runtime/review-extension-development/`, результаты — verify-notes при
реализации; этот planning pass не запускает тесты и не утверждает их успех.

## Risks / Trade-offs

- Защищённая граница сложнее локального waiver → default 2 работает без неё;
  исключение явно требует отдельного host setup, который не выполняет installer.
- Coordinator/worker isolation меняет execution envelope → exact bridge и
  реальный multi-UID тест обязательны до заявления installed compatibility.
- Локальный ledger можно удалить → authoritative state у broker, потеря истории
  блокирует работу; восстановление backup не должно уменьшать счётчики.
- Broker хранит чувствительные пути/findings → минимальный protocol, restricted
  state directory, redaction; эти файлы не входят в Git/runtime release.
- Pause не отменяет внешние effects → контролируется следующий переход,
  фактические effects сохраняются, publication authority проверяется отдельно.
- Allowlist путей не доказывает корректность repair → finding-bound handoff,
  актуальные регрессии и независимый review №3 обязательны.

## Migration Plan

1. Реализовать policy и regressions без изменения default 2; создать защищённый
   broker/client и отрицательные проверки неподдержанного contour.
2. Доказать all-gate accounting, atomic recovery и multi-UID trust boundary.
3. Добавить точные rc.2/rc.3 descriptors и synthetic installed end-to-end.
4. Обновить AGENTS/config/README/specs/runbooks/skills согласованно: default 2,
   единственное +1, предел 3; обновить release packaging и CI dependencies.
5. После независимого review и release оператор отдельно устанавливает новый
   runtime и при необходимости authority contour. Реальный grant всегда
   привязан к конкретному просмотренному proposal; установка не выдаёт grant.

Rollback до reservation допустим только по точному installation audit без
восстановления старого исполнения. После grant/reservation ledger не удаляют:
cancel или остановка сохраняют расход; старый runtime не возобновляет lineage.

## Open Questions

Незакрытых продуктовых решений для реализации нет. UID, каталоги broker и
конкретный host isolation launcher выбирает оператор при подключении потребителя;
это параметры deployment, а не неявные defaults. Если реализация не может
доказать описанную OS-границу или exact installed bridge, соответствующий путь
остаётся fail-closed; не заменять требование одним локальным `approved` файлом.
