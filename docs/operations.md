# Руководство оператора

Первоначальная установка и принятие карточки описаны в [quickstart](quickstart.md).
Здесь приведены обычный запуск и действия после остановки. Команды работают
с репозиторием потребителя, который владеет профилем, board, OpenSpec change,
продуктовым кодом и `.runtime/`.

## Выбор проекта и запуск

Во всех примерах явно выбирается потребитель; замените значения своими.
`--project` должен стоять перед именем команды. Относительные пути после него
считаются от корня выбранного проекта.

```sh
chrl_project=/opt/example-project
chrl_run=.runtime/changerail/runs/REPLACE_WITH_RUN_ID
chrl_card=openspec/board/2.todo/REPLACE_WITH_CARD.md
"$chrl_project/bin/chrl" --project "$chrl_project" wiring
"$chrl_project/bin/chrl" --project "$chrl_project" doctor "$chrl_card"
```

`wiring` проверяет подключение инструмента и зависимостей. `doctor` проверяет
готовность конкретной карточки: принятый native plan, профиль и команды,
чистый проект, ветку `main` и настроенный upstream. По умолчанию проверяется
доступность удалённой ветки. `doctor --no-remote` пропускает сетевую проверку,
поэтому его успех не доказывает готовность push. Эти команды не запускают доставку.

До нового запуска сохраните исходное состояние проекта обычным коммитом:
рабочее дерево и index должны быть чистыми, карточка — принятой и находиться
в `2.todo`. Проверьте адрес push и доступ к upstream; автоматической настройки
удалённого репозитория нет. Должен быть ровно один push URL выбранного remote.

```sh
git -C "$chrl_project" status --short
git -C "$chrl_project" branch --show-current
git -C "$chrl_project" rev-parse --abbrev-ref --symbolic-full-name '@{u}'
git -C "$chrl_project" remote -v
"$chrl_project/bin/chrl" --project "$chrl_project" run "$chrl_card"
```

`run` начинает одну доставку: одна карточка, один OpenSpec change, реализация,
не более двух независимых ревью с общим остатком на repair, archive и финальные
проверки. Время — наблюдение. Runner удерживает локальную блокировку проекта.

Успешная доставка **сама выполняет commit и push**. После GO и проверок runner
переносит карточку в `4.done`, обновляет ссылки board и добавляет в index точную
проверенную выборку продукта, OpenSpec и карточки. Посторонний diff блокирует
публикацию. Commit создаётся в потребителе; push отправляет его точный SHA
в настроенный upstream. Общий checkout ChangeRail не входит в этот commit.
`require_push = false` влияет на сетевую проверку `doctor`, но **не отключает push**
в публикации. Аналогично `require_clean_start` не предоставляет режим работы
поверх посторонних изменений. Полномочия Codex launcher описаны в [SECURITY.md](../SECURITY.md).

## Сначала диагностика

Идентификатор run берите из вывода runner и каталога `.runtime/changerail/runs/`.
Не выбирайте предшественника только по времени изменения каталога.

```sh
"$chrl_project/bin/chrl" --project "$chrl_project" status "$chrl_run"
git -C "$chrl_project" status --short
cat "$chrl_project/$chrl_run/run.json"
```

`status` читает сохранённые checkpoint и последнее событие; он не доказывает,
что процесс завершён, код совместим или продолжение разрешено. Проверьте процесс
runner и его дочерние процессы средствами управления той сессией, где он был
запущен. Наличие файла `delivery.lock` само по себе не означает живого владельца:
не удаляйте файл блокировки для обхода работающего процесса.

После остановки сохраните в закрытом локальном каталоге копию `.runtime/changerail/`,
`.changerail/`, Git HEAD и status, staged/unstaged diff и все затронутые untracked
файлы. Сохраните и состояние общего исходника, если использовались ссылки.
Для аварии установки дополнительно нужны исходный архив и его SHA-256.
Backup должен сохранять режимы файлов и сами ссылки, без разыменования.
Профиль, журналы и evidence могут содержать локальные данные: они остаются
у потребителя и не входят в публичный отчёт.

## Обычное продолжение

При остановленной реализации и неизменных frozen identity, принятом плане
и точном сохранённом payload используйте выбранный run:

```sh
"$chrl_project/bin/chrl" --project "$chrl_project" resume "$chrl_run"
```

`resume` проверяет предшественника и создаёт recovery run с `recovery_of`,
наследует checkpoints, evidence и израсходованное ревью. Это не новый бюджет.
Карточка остаётся в `3.inprogress`, index должен быть пустым; незакоммиченный
payload обязан совпадать с сохранённым manifest. Для отдельной предварительной
проверки используйте `doctor` с путём карточки в `3.inprogress`, `--recovery`
и переменной `CHRL_RECOVERY_OBJECTIVE`, содержащей конкретную цель продолжения.
Обычный `resume` задаёт цель по умолчанию, если переменная не установлена.

Изменение кода, профиля, схем, skills, launcher или контура OpenSpec блокирует
обычное продолжение. Для исправления только Python-ядра общего исходника есть
[runtime repair](runtime-repair.md), допустимый лишь для остановленного первичного
native run до первого принятого checkpoint, evidence и поздних этапов.
Он не распространяется на локальную runtime-копию и исторические runs.
Для drift принятого Next предусмотрен отдельный ограниченный переход ниже,
в том числе с проверяемым обновлением установленного runtime. Вне документированных
границ сохраните состояние для разбора; не переписывайте `run.json` и receipts.

Исторические `delivery-runs`, `ff-runs`, `offline-finalizations` доступны для
чтения через `status`; они не получают права на native resume после обновления.
Порядок сохранения истории при установке — в [DISTRIBUTION.md](../DISTRIBUTION.md).

## Восстановление принятого Next

Если реализация изменила frozen `Next`, возврат текста вручную нарушает точный
сохранённый payload. Команды `plan-restore-prepare` и `plan-restore-apply`
восстанавливают принятые байты Next и сохраняют переход отдельно от истории runs.
Другие frozen sections и OpenSpec artifacts должны соответствовать принятому
плану; изменения только checkboxes не меняют семантику задач. Текущие Result/Log
и режим карточки сохраняются.

Выберите точный stopped run по его `run.json`, включая последнюю неудачную
попытку resume. Предок может содержать принятый план, отсутствующий у failed child;
добавлять план в старый child не нужно. До prepare должны совпадать Git HEAD,
пустой index, сохранённый manifest и вся ancestry. Причина остановки должна быть
drift принятого плана или связанный отказ до импорта.

Для runtime с прежней frozen identity:

```sh
"$chrl_project/bin/chrl" --project "$chrl_project" plan-restore-prepare "$chrl_run" \
  --reason 'Восстановление принятого Next после implementation drift' --dry-run
"$chrl_project/bin/chrl" --project "$chrl_project" plan-restore-prepare "$chrl_run" \
  --reason 'Восстановление принятого Next после implementation drift'
```

Dry-run не пишет proposal. Обычный prepare возвращает `proposal` и
`proposal_sha256`. Просмотрите сохранённый diff, before/after hashes, lineage,
принятый источник и reason. Apply разрешает только эту точную операцию:

```sh
"$chrl_project/bin/chrl" --project "$chrl_project" plan-restore-apply "$chrl_run" \
  --proposal .runtime/changerail/plan-restorations/REPLACE_WITH_ID/proposal.json \
  --authorize REPLACE_WITH_PROPOSAL_SHA256
"$chrl_project/bin/chrl" --project "$chrl_project" resume "$chrl_run"
```

Подставьте значения из prepare; SHA-256 — полномочие на конкретный proposal.
Prepare/apply выполняются вне implementation/review-сессии и удерживают project
lock. Apply не запускает runner. После него обычный resume создаёт единственного
successor с `recovery_of` на выбранную последнюю попытку. Завершённые группы
не повторяются; focused/observed proofs необходимо обновить перед handoff.
Старые run.json, manifests, evidence, events и счётчики не переписываются.

Для установленной копии прежней версии запускайте **новый проверенный runtime
из отдельного каталога** с явным `--project`, пока у потребителя ещё установлен
старый комплект. Целевой архив обязан содержать точные байты этого нового runtime:

```sh
chrl_tool=/opt/example-changerail-next
chrl_archive=/opt/example-releases/changerail-2.0.0-rc.3-runtime.tar.gz
"$chrl_tool/bin/chrl" --project "$chrl_project" plan-restore-prepare "$chrl_run" \
  --reason 'Восстановление Next с проверяемым переходом установленного runtime' \
  --runtime-archive "$chrl_archive"
"$chrl_tool/bin/chrl" --project "$chrl_project" plan-restore-apply "$chrl_run" \
  --proposal .runtime/changerail/plan-restorations/REPLACE_WITH_ID/proposal.json \
  --authorize REPLACE_WITH_PROPOSAL_SHA256
"$chrl_project/bin/chrl" --project "$chrl_project" resume "$chrl_run"
```

Совместимость ограничена native predecessor `2.0.0-candidate.5`, `2.0.0-rc.1`
и `2.0.0-rc.2` с доказанными schemas, identity shape и полным frozen distribution
lock. Одной строки версии недостаточно. Профиль, launcher и адаптеры потребителя
не должны изменяться. Неполный старый process identity допускается только там,
где старый frozen lock доказывает пропущенные tool bytes и точный payload
входит в поставляемый compatibility descriptor. Самосогласованный неизвестный
fork с той же строкой версии отклоняется. Несвязанные frozen runs
блокируют переход; read-only history никогда не получает право resume.
Обычный install и `--retain-history-read-only` не заменяют эту операцию.

При прерывании apply повторите **тот же apply с тем же proposal и SHA-256**.
Durable intent позволяет согласовать только доказанные before/after состояния
карточки и old/target состояния файлов runtime. Любое третье состояние требует
разбора. Незавершённый intent блокирует обычный run/resume до согласования;
не удаляйте его и не создавайте новый proposal для обхода. Успешный повтор apply
не делает второй переход. Создание successor также имеет durable intent: полный набор run/plan/manifest/context
сначала готовится отдельно и атомарно появляется в каталоге runs. Если resume
прервался до начала исполнения successor, повторите resume выбранного predecessor:
он завершит создание того же run. После начала successor используйте его обычный
status и resume. Архив target сохраняйте доступным до завершения apply.

Не поддерживаются остановка оператором, unresolved verification attempt,
незавершённый provisional review, archive intent/archive, final floor и публикация.
Законченный NO-GO допустим при оставшемся бюджете; после двух ревью prepare
отклоняется. Переход не устраняет посторонние ошибки board и не обходит дальнейшие
sync, handoff, review, archive, final и publication gates. Если прежний manifest
уже переписан вручную, нельзя объявлять его исходным сохранённым evidence.

## Прерванная или неуспешная проверка

Если оператор остановил проверку, не запускайте её полный набор заново.
Сохранённая попытка без доказанного terminal result остаётся unresolved;
обычное recovery не перезапускает её и не считает отсутствие результата успехом.
Не удаляйте `verification-attempts`, логи, index и receipts для получения новой
попытки. Поддерживаемой команды, которая автоматически разрешает такое состояние,
нет; нужен разбор сохранённого процесса и доказательств.

Завершившаяся с ошибкой проверка — другой случай. Для того же неизменного payload
повторный финальный набор и новое ревью запрещены. Продолжение ремонта использует
сохранённый результат и логи, исправляет причину ошибки, обновляет затронутое
evidence и расходует только оставшийся общий лимит ревью. Не повторяйте уже
завершённые Change checkpoints ради нового запуска.

## Archive и публикация

Прерванный archive сохраняет неизменный `native-archive-intent.json`. Если
перемещение ещё не выполнено, а дата UTC сменилась, обычное продолжение после
проверок HEAD, payload и отсутствия конфликтующих каталогов добавляет связанный
хешем successor intent. Уже выполненное точное перемещение проверяется по
сохранённому назначению. Если дата сменилась внутри самой команды stock archive,
автоматического выбора нового назначения нет. Не перемещайте каталоги вручную
для обхода проверки; подробности — в [migration.md](migration.md).

Если `publication.json` имеет состояние `committed`, `resume` использует отдельный
путь: проверяет frozen identity, точные HEAD, tree, parent, чистое дерево,
направление push и хеши evidence, затем повторяет push того же commit.
Нового commit, ревью и тестового запуска он не создаёт. Исправляйте причину
сетевого отказа, сохраняя ветку, commit и назначение. Состояние `pushed` возвращает
успех после проверок, без повторного push.

Состояние публикации `prepared` ещё не доказывает завершённый commit; даже если
Git commit фактически успел появиться до сбоя, `resume` отклоняет его без
`committed` receipt. Автоматического восстановления этой границы нет. Сохраните
Git refs, index и `publication.json`; не переписывайте receipt по предположению.

## Незавершённая установка или подключение

Установку и изменение shared source выполняйте после завершения всех затронутых
runner. Новые процессы видят новые байты, старые продолжают использовать уже
загруженный Python; гарантированной автоматической остановки на границе этапа нет.

Для copy-install найдите audit по SHA-256 архива:

```sh
cat "$chrl_project/.runtime/changerail/distribution/REPLACE_WITH_ARCHIVE_SHA256/audit.json"
cat "$chrl_project/.changerail/distribution-lock.json"
```

| Audit state | Значение и действие |
| --- | --- |
| `installed` | Установщик завершил замену; проверьте `wiring`, lock и рабочее дерево. |
| `rolled_back` | Перехваченная ошибка, предыдущие bytes, режимы и lock восстановлены; изучите `failure` и сохранённый backup. |
| `rollback_failed` | Откат не завершён; изучите `rollback_errors`, не запускайте runtime. |
| `prepared` или audit отсутствует | Завершение транзакции не доказано; возможен частичный набор файлов. |

При двух последних состояниях сначала сохраните фактические файлы и backup
`before/`, `previous-lock.json`, audit и разрешения adoption/history, если они
есть. Сверьте списки created/replaced/removed из audit с архивом и предыдущим
lock. Отсутствие ошибки в старом логе не доказывает восстановление.

Повторная изменяющая установка того же архива не может занять уже существующий
audit-каталог даже после `rolled_back`. Команды автоматического rollback/reconcile
нет. Не удаляйте audit-каталог и не переписывайте lock, inventory или историю
для повтора. При незавершённом состоянии специалист должен отдельно согласовать
восстановление точных предыдущих файлов либо корректное завершение установки,
сохранив исходные доказательства и отчёт о каждом изменении. Критерий результата —
полная согласованность установленных байтов и режимов с выбранным lock и сохранная
история. Для восстановленного установленного runtime дополнительно нужен успешный
`wiring`; при возврате к состоянию без ChangeRail его файлы и installation lock
должны отсутствовать, как до попытки. Один успешный импорт Python недостаточен.

Shared-source использует другой audit в `.runtime/changerail/source-bindings/`:
`attached` после успешного подключения, `rolled-back` после завершённого отката.
`detach --dry-run` и `detach` поддерживают восстановление только при корректных
binding, audit, backup и **неизменном inventory runs с момента attach**.
Любой новый run, включая завершённый, блокирует detach; команды reconciliation
пока нет. При незавершённом attach или detach сохраняйте сами ссылки и backup
и выполняйте отдельный разбор, не подменяя audit. Команды и точные ограничения
приведены в [shared-source.md](shared-source.md).
