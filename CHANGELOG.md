# Изменения

## 2.0.0-rc.5 — release executor и совокупные test proofs

- Отдельный принятый release checkout исполняет будущие runs dev-проекта;
  `release-update` и `executor-bind` сохраняют проверяемые receipts и поддерживают
  reconcile без изменения истории и без новых полномочий resume старых runs.
- Test method допускает необязательные `additional_targets`; совокупность
  singleton proofs покрывает все объявленные targets. Одно исполнение может
  поддерживать несколько условий, assertions — оставаться в вызываемом helper.
- Сохранены текущие identity/freshness/selection проверки и совместимость прежних
  singleton proofs. Новый формат требует совместимого engine до принятия плана.
- `tools/openspec/.gitignore` исключён из runtime payload и source-link inventory;
  исключения зависимостей задаются у потребителя.

Это подготовленный кандидат; CI точного release commit и публикация выполняются
отдельно. Подробности — в [release notes](docs/releases/2.0.0-rc.5.md).

## 2.0.0-rc.4 — изолированный engine и self-host recovery

- Отдельный immutable engine с inventory, проверяемой identity и явным binding;
  rebind меняет engine через сохраняемую транзакцию.
- Self-host prepare/apply/reconcile создаёт единственный successor атомарно,
  сохраняет ancestry, evidence, completed groups и общий остаток двух ревью.
- Поддержано продолжение после технического сбоя модели и проверенной
  финализации, включая повторный resume bound successor после commit.
- Recovery/finalize требует прочитать конкретный objective, завершить Result/Log
  до свежих receipts и записать observed proofs перед handoff.
- Уточнены роли checkout, consumer binding, повторное применение,
  границы отката и сохранение рабочего checkout при обновлении.

Подробности — в [release notes](docs/releases/2.0.0-rc.4.md).

## 2.0.0-rc.3 — точное восстановление принятого плана

- Prepare/apply для восстановления frozen Next с отдельной неизменяемой
  транзакцией; история runs и неудачных resume сохраняется полностью.
- Явный переход поддержанного installed predecessor на точный новый архив,
  без предоставления права исполнения read-only истории.
- Продолжение сохраняет completed groups и review budget, требует свежие proofs
  и проходит обычные handoff, review, archive, final и publication gates.
- Новые admissions сохраняют accepted-card snapshot; implementing skill явно
  запрещает менять frozen sections и объявлять успех при отказе handoff.
- Документированы команды восстановления, прерывания apply и границы миграции.

Подробности — в [release notes](docs/releases/2.0.0-rc.3.md).

## 2.0.0-rc.2 — документация и эксплуатация

- Quickstart для опубликованного архива и первой native-доставки.
- Runbooks эксплуатации, восстановления и выпуска релиза.
- Исправлены примеры выбора проекта при repair и описание ограничений detach.
- Описаны полномочия launcher, shell-окружение и финальный commit/push.
- Русский OpenSpec README, актуальные ссылки и сведения о публикации rc.1.
- Review skill использует доступные инструкции потребителя без обязательного
  board README; это изменение влияет на frozen identity старых запусков.

Подробности — в [release notes](docs/releases/2.0.0-rc.2.md).

## 2.0.0-rc.1 — 2026-09-10 — общий native runtime

- Один OpenSpec change на карточку; общий предел двух независимых ревью.
- Типизированные evidence, read-only история, доказанное восстановление.
- Runtime-копия и общий рабочий исходник; тесты доступны разработчикам.
- Исправление инструмента отделено от продуктового payload.
- Linux-native установка; прежние FF/offline/Windows исполнители удалены.
- Frozen identity учитывает загрузчики и установочные файлы OpenSpec, а также
  файл инициализации пакета Python; изменения через общие ссылки блокируют resume.
- Attach проверяет ignore до записи runtime; detach восстанавливает проверенный
  backup даже после перемещения или удаления общего исходника.
- Прерванный до перемещения archive может продолжиться в следующие UTC-сутки
  через цепочку квитанций, сохраняя исходный intent и review accounting.
- Адаптер OpenSpec выбирает Node из PATH; Ruff выполняется в CI.

[Предварительный релиз опубликован](https://github.com/vlikhobabin/changerail/releases/tag/v2.0.0-rc.1)
из `eba4000`; полный CI прошёл на Python 3.11 и 3.12. Stable 2.0.0 ещё не выпускался.
Предыдущие версии и changelog доступны в Git и тегах до 2.0.0.
