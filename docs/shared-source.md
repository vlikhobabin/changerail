# Общий рабочий исходник

Клонируйте ChangeRail в любой каталог и установите зависимости по CONTRIBUTING.
В командах ниже текущий каталог — корень ChangeRail; `/opt/example-project` —
отдельный Git-проект с локальным `.changerail/profile.toml` и `.runtime/` в ignore.
Начальный профиль доступен в `tools/changerail/templates/profile.toml`: замените
команды проверки реальными командами продукта и задайте свой Codex launcher.
OpenSpec config и board принадлежат проекту и создаются явно до первой доставки.

## Исходник, выпуск и engine

Dev-checkout хранит разрабатываемые исходники ChangeRail. Рабочий checkout может
быть закреплён на опубликованном release tag и обновляется отдельно. Каждый
consumer выбирает один из этих каталогов собственным `.changerail/source-link.json`.
Это связь с адресом исходника: последующие правки по этому адресу становятся
доступны новым процессам потребителя без повторного attach. Публикация release,
обновление другого checkout и замена self-host engine не переключают consumer.
Режим `--development` добавляет ссылки на тестовые инструменты; он не закрепляет
Git revision и не создаёт отдельную копию runtime.

Для self-host доставки нужен четвёртый отдельный каталог — immutable engine
snapshot. Его `.changerail/engine-binding.json` принадлежит self-host проекту,
а inventory и `engine_identity` подтверждают точные bytes и режимы snapshot.
Изменяемый dev-checkout служит продуктом доставки, snapshot — её исполнителем.
Общий source binding потребителя и engine binding self-host проекта имеют разные
назначения. Snapshot никогда не обновляют на месте; подготовка и явный rebind
описаны в [self-host runbook](self-host-recovery.md).

## Подключение

Для пустой установки:

```sh
python3 distribution.py attach /opt/example-project --dry-run
python3 distribution.py attach /opt/example-project
```

Для замены существующего комплекта требуется точная инвентаризация. Она включает
источник, заменяемые файлы и старые runs, которые сохраняются read-only:

```sh
python3 distribution.py attach-inventory /opt/example-project --development \
  --output /tmp/changerail-attach.json
python3 distribution.py attach /opt/example-project --development \
  --adoption /tmp/changerail-attach.json --dry-run
python3 distribution.py attach /opt/example-project --development \
  --adoption /tmp/changerail-attach.json
/opt/example-project/bin/chrl wiring
```

`--development` подключает также общие тесты, test launcher и OpenSpec wrapper
tests. Профиль проекта, его `.changerail/tests/`, `bin/codex`, node_modules и
evidence не копируются из общего checkout. Потребитель выбирает собственные
зависимости OpenSpec явным bootstrap; существующая установка сохраняется.

Ссылки и их ожидаемые назначения записываются в `.changerail/source-link.json`.
Замена ссылки посторонней целью блокирует wiring и исполнение. Изменение байтов
в доверенном исходнике допускается; wiring сообщает Git revision, dirty и hash.
При запуске из вложенного каталога используется Git-корень проекта. При явном
выборе: `bin/chrl --project /opt/example-project wiring`.

## Разработка из проекта

Откройте `scripts/changerail/<module>.py` через путь подключённого проекта.
Правка меняет файл ChangeRail; новые команды всех его потребителей используют
эту правку. `git -C /path/to/changerail status` показывает изменения инструмента.
Используйте `bin/test-changerail -k <regression>` для сфокусированной проверки.
Общие тесты выполняются на исходнике; отдельные `.changerail/tests/` проверяют
только профиль текущего проекта. Полный набор не запускается автоматически.

Прикладная доставка не коммитит общий исходник. Сначала сохраните исправление
в ChangeRail с регрессией, затем коммитьте продуктовый payload в его репозитории.
Уже работающий процесс не получает новые Python-модули автоматически.

## Продолжение после исправления

Поддержано ограниченное продолжение остановленной первой implementation-сессии
до принятых checkpoints, evidence, handoff, review, archive и floor. Менять можно
Python-код ядра; профиль, схемы, skills и launcher остаются замороженными.
Это не снимает защиту поздних этапов, где нужен повторный анализ доказательств.

```sh
./bin/chrl --project /opt/example-project runtime-repair-prepare .runtime/changerail/runs/REPLACE_WITH_RUN_ID \
  --test tools/changerail/tests/test_example.py::test_regression \
  --reason 'исправление воспроизведённой ошибки инструмента'
./bin/chrl --project /opt/example-project runtime-repair-apply .runtime/changerail/runs/REPLACE_WITH_RUN_ID \
  --proposal /absolute/path/from/prepare.json
./bin/chrl --project /opt/example-project resume .runtime/changerail/runs/REPLACE_WITH_RUN_ID
```

Prepare реально исполняет указанную регрессию, сохраняет source snapshot,
вывод и старую/новую идентичность. Apply проверяет неизменность и добавляет
receipt. Старый run.json не переписывается. История, review accounting и обычные
gates остаются обязательными; исторические runs таким способом не возобновляются.
`--project` выбирает потребителя и его `.runtime/`, даже когда команда запущена
из checkout инструмента. Путь `--test` относится к общему исходнику; подставьте
существующую регрессию. Подробные ограничения — в [runtime-repair.md](runtime-repair.md),
выбор способа продолжения — в [руководстве оператора](operations.md).

## Отключение и восстановление

Перед изменением binding сохраните локальные профиль, настройки, credentials,
board, всю `.runtime/changerail/`, Git HEAD/index/diff и untracked работу в закрытом
backup с байтами, режимами и ссылками без разыменования. Отдельно зафиксируйте
состояние общего checkout. Сохранённые manifests, checkpoints, evidence и review
accounting не подменяются новым inventory. Проверьте отсутствие работающих runner.
Не удаляйте `delivery.lock` ради подключения.

```sh
python3 distribution.py detach /opt/example-project --dry-run
python3 distribution.py detach /opt/example-project
```

Detach восстанавливает прежние файлы из сохранённого backup только при **точном
совпадении inventory runs с моментом attach**. Добавление, удаление или изменение
любого учитываемого `run.json`, включая новый успешно завершённый run, блокирует
операцию сообщением `runs changed since attach; detach requires reconciliation`.
Проверка учитывает пути, байты и режимы файлов из `runs`, `delivery-runs`, `ff-runs`
и `offline-finalizations`. Поддерживаемой команды reconciliation пока нет:
не удаляйте runs и не переписывайте inventory ради прохождения проверки.
Сохраните состояние и передайте его на разбор по [руководству оператора](operations.md).

При неизменном inventory восстановление работает и после перемещения или удаления
общего checkout: запускайте команды выше из доступного checkout ChangeRail.
Отсутствующий исходник не мешает проверке точных адресов ссылок, сохранённого
inventory, audit и байтов backup. Подменённые ссылки, ссылки в родительских
каталогах и изменённый backup останавливают восстановление до замены файлов.
Обычный запуск runtime по-прежнему требует доступный и проверенный исходник.
Исправления общего исходника остаются в ChangeRail.
Attach, включая `--dry-run`, проверяет Git ignore для `.runtime/` до создания
lock и backup; сначала добавьте `.runtime/` в ignore потребителя.
Attach удерживает delivery.lock, сохраняет backup и пытается откатить перехваченные
ошибки. Успешное подключение записывает audit `attached`, завершённый откат —
`rolled-back`. Потеря питания или ошибка самого отката могут оставить частичные
ссылки и backup без завершённого audit. Общей транзакции файловой системы нет;
`detach` требует корректные binding, inventory и audit успешного attach и не
является универсальной командой аварийного восстановления. Сохраните содержимое
`.runtime/changerail/source-bindings/` и текущее состояние проекта перед разбором.

## Проверка обновления и повторное применение

После обновления выбранного общего checkout проверьте его точный release commit
и diff, затем выполните `bin/chrl --project /opt/example-project wiring` для каждого
затронутого binding. Сверьте `.changerail/source-link.json`, назначение и режимы
ссылок, локальный профиль, зависимости и сохранённый inventory данных с backup.
Успех wiring подтверждает подключение, но не совместимость frozen runs с новым
кодом. Старые процессы Python не подхватывают обновление автоматически.

Для переноса потребителя на другой source нет команды `rebind`: `engine-rebind`
меняет только self-host engine. Используйте проверяемый `detach --dry-run`/`detach`
и затем новый attach с актуальным inventory, если каждый шаг разрешён контрактом.
Если runs изменились после attach, detach блокируется: перестановка ссылок вручную
не является поддержанным переключением. Не применяйте copy-install поверх ссылок.

Повторный attach и новый adoption не являются восстановлением незавершённой
операции. При частичных ссылках или незавершённом audit сначала сохраните состояние
для разбора по [руководству оператора](operations.md#незавершённая-установка-или-подключение).
Поддержанный detach возвращает только сохранённые до attach файлы потребителя;
он не откатывает общий checkout и не отменяет доставку. Возврат исходника к прежней
версии также не стирает новые runs и не разрешает их продолжение другой identity.
Общие тесты ChangeRail выполняются в его исходном репозитории, а не при каждом
подключении и не в consumer-проектах.
