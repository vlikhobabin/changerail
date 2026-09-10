# Общий рабочий исходник

Клонируйте ChangeRail в любой каталог и установите зависимости по CONTRIBUTING.
В командах ниже текущий каталог — корень ChangeRail; `/opt/example-project` —
отдельный Git-проект с локальным `.changerail/profile.toml` и `.runtime/` в ignore.
Начальный профиль доступен в `tools/changerail/templates/profile.toml`: замените
команды проверки реальными командами продукта и задайте свой Codex launcher.
OpenSpec config и board принадлежат проекту и создаются явно до первой доставки.

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
./bin/chrl runtime-repair-prepare .runtime/changerail/runs/<run> \
  --test tools/changerail/tests/test_example.py::test_regression \
  --reason 'исправление воспроизведённой ошибки инструмента'
./bin/chrl runtime-repair-apply .runtime/changerail/runs/<run> \
  --proposal /absolute/path/from/prepare.json
./bin/chrl resume .runtime/changerail/runs/<run>
```

Prepare реально исполняет указанную регрессию, сохраняет source snapshot,
вывод и старую/новую идентичность. Apply проверяет неизменность и добавляет
receipt. Старый run.json не переписывается. История, review accounting и обычные
gates остаются обязательными; исторические runs таким способом не возобновляются.

## Отключение и восстановление

```sh
python3 distribution.py detach /opt/example-project --dry-run
python3 distribution.py detach /opt/example-project
```

Detach восстанавливает прежние файлы из сохранённого backup и отказывается при
несовместимых новых runs. Восстановление работает и после перемещения или удаления
общего checkout: запускайте команды выше из доступного checkout ChangeRail.
Отсутствующий исходник не мешает проверке точных адресов ссылок, сохранённого
inventory, audit и байтов backup. Подменённые ссылки, ссылки в родительских
каталогах и изменённый backup останавливают восстановление до замены файлов.
Обычный запуск runtime по-прежнему требует доступный и проверенный исходник.
Исправления общего исходника остаются в ChangeRail.
Attach, включая `--dry-run`, проверяет Git ignore для `.runtime/` до создания
lock и backup; сначала добавьте `.runtime/` в ignore потребителя.
Attach удерживает delivery.lock, сохраняет backup и откатывает перехваченные
ошибки. Потеря питания не является атомарной транзакцией всей файловой системы;
для восстановления используйте audit и backup под `.runtime/changerail/source-bindings/`.
