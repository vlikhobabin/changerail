# Собственная доставка ChangeRail

При разработке самого ChangeRail продуктовый checkout изменяется, а исполняемый
engine остаётся закреплённым. Чистый Git checkout и символическая ссылка не
обеспечивают этот контракт. Для engine нужен отдельный snapshot с полным inventory
и локальным `.changerail/engine-binding.json`.

Роли dev, рабочего checkout, engine и consumer binding описаны в
[руководстве оператора](operations.md#разработка-самого-changerail).
Обновление опубликованной версии рабочего checkout выполняется по
[отдельному runbook](working-checkout.md), с сохранением локальной истории.

## Подготовка engine

Сначала проверьте и закоммитьте изменения инструмента. Snapshot создаётся только
из чистого committed source и содержит публичную distribution-выборку: Python,
launchers, schemas, skills и OpenSpec helpers. Git, профили, credentials, журналы
и зависимости в snapshot не переносятся. Каталоги ниже произвольны:

```sh
chrl_source=/srv/tools/changerail-dev
chrl_engine=/srv/engines/changerail/verified-candidate
"$chrl_source/bin/chrl" --project "$chrl_source" engine-snapshot-create "$chrl_engine"
"$chrl_source/bin/chrl" --project "$chrl_source" engine-snapshot-verify "$chrl_engine"
"$chrl_source/bin/chrl" --project "$chrl_source" engine-bind "$chrl_engine"
```

Read-only permissions предотвращают случайную запись. Перед исполнением runner
также проверяет полный inventory, включая режимы, добавленные и удалённые файлы.
Python запускается с точным `PYTHONPATH` и без импорта из текущего каталога.
Вложенные команды используют `"$chrl_engine/bin/chrl" --project "$chrl_source"`.
Schemas и инструкции skills читаются из snapshot. Профиль, model launcher,
проектные adapters, Python и установленная локальная OpenSpec dependency входят
в отдельную identity execution inputs. Изменение этих входов блокирует продолжение.

Binding не разрешает продолжать старый run новым кодом. Для такого перехода
обязателен отдельный self-host receipt. Повторный `engine-bind` идемпотентен только
для того же snapshot; другая identity не подменяется молча.

## Явная замена engine

Если требуется исправить закреплённый engine, создайте новый проверенный snapshot.
Запускайте замену из него, указав точную прежнюю `engine_identity` из binding:

```sh
chrl_next_engine=/srv/engines/changerail/verified-correction
chrl_previous_identity=REPLACE_WITH_PREVIOUS_ENGINE_IDENTITY
"$chrl_next_engine/bin/chrl" --project "$chrl_source" engine-rebind \
  --previous-identity "$chrl_previous_identity"
```

Операция выполняется вне delivery, под delivery lock и после проверки отсутствия
живых владельцев. Обе snapshots проверяются; intent сохраняет точные before/after
binding до атомарной замены. Applied receipt связывает intent с новым binding.
Receipts находятся в `.runtime/changerail/engine-rebind/`. После crash повторите
ту же команду: она завершит тот же переход. Drift receipts, binding или snapshots
отклоняется. Старые run.json не изменяются и не получают новую execution identity.

Для остановленного bound successor новый self-host переход готовится именно от
него. Он разрешён в том же project root при неизменных project execution inputs,
включая локальные зависимости и Python; исключение составляет явно заменённый
engine binding. Повторять apply первоначального predecessor не следует.

## Переход остановленного run

Поддерживается native run, остановленный после завершения всех task groups до
review, final verification, archive и publication. Принятый план должен совпадать.
Operator stop, неизвестная session state, живые процессы, незавершённая проверка,
чужой проект, symlink и занятый delivery lock отклоняются.

Исторический capacity failure допускается только при наличии проверенных
technical recovery proposal, applied receipt и successor intent, которые связывают
точную сессию и неизменную историю с уже завершившим группы successor.
Необработанный nonzero exit не даёт права на self-host переход.

Если после остановки изменился payload, подготовьте локальный каталог с исходными
байтами и режимами файлов, соответствующими `manifest.json`. Отсутствующие файлы
обозначают сохранённые удаления. Источником могут быть Git baseline и сохранённые
patches, но результат принимается только при совпадении всех fingerprint.
Нельзя заменять отсутствующие исходные байты текущим содержимым или угадывать их.

```sh
chrl_previous=/srv/tools/changerail/.runtime/changerail/runs/REPLACE_WITH_RUN_ID
chrl_before=/srv/local-evidence/stopped-payload
"$chrl_engine/bin/chrl" --project "$chrl_source" self-host-recovery-prepare \
  "$chrl_previous" --payload-snapshot "$chrl_before"
# Используйте точный путь proposal, который вернула предыдущая команда.
"$chrl_engine/bin/chrl" --project "$chrl_source" self-host-recovery-apply \
  "$chrl_previous" --proposal "$chrl_source/.runtime/changerail/self-host-recoveries/REPLACE_WITH_RUN_ID/proposal.json"
"$chrl_engine/bin/chrl" --project "$chrl_source" self-host-recovery-reconcile "$chrl_previous"
```

Receipt связывает исходный и новый checkout, весь inventory predecessor и ancestry,
принятый план, engine, project inputs, исходные bytes и corrective diff. История
копируется атомарно с сохранением байтов; оригинальные run.json и evidence не
редактируются. Обе стороны перехода блокируются, а reservation у origin запрещает
второй successor из другого checkout.

Successor получает completed groups и прежний review accounting, начинает fresh
finalize и проходит обычные review, archive, final verification и publication.
Прежний sync и proof не становятся актуальными доказательствами нового payload.
Повторный apply/reconcile согласует прежний successor и не запускает writer снова.
После зафиксированного dispatch и последующей terminal остановки применяется
обычный `resume` successor с сохранённой engine identity. Пустой payload после
коммита допускается только при точном выборе retained self-host run и совпадении
HEAD, manifest и fingerprints; reservation, dispatch и исходная история должны
оставаться целыми. Автоматический поиск по пустому payload запрещён. Неоднозначный dispatch
не является разрешением на повтор исполнения.

## Подключение потребителей

Переход self-host run не переключает consumer-проекты. После проверки результата
каждый проект подключается отдельной операцией `distribution.py attach --development`
по [контракту shared source](shared-source.md). Inventory создаётся непосредственно
перед применением и сохраняется локально. Занятый delivery lock требует дождаться
его владельца; удалять lock или останавливать чужой run ради установки нельзя.

## Результат и границы отката

Перед handoff завершите Result/Log, получите свежие receipts и запишите observed
proofs всех назначенных implementation conditions. Прочитайте objective из
`CHRL_RECOVERY_CONTEXT`; успешный evidence не заменяет proof. Проверяйте terminal
результат successor, review, archive, финальные проверки и receipt публикации,
а также неизменность ancestry. Reconcile не является подтверждением доставки.

Snapshot не обновляют на месте. Обратный выбор сохранённого engine — отдельный
`engine-rebind` из него с текущей previous identity, при прохождении всех guards
и retained intents. Он не отменяет reservation/dispatch, не возвращает право
запуска predecessor и не откатывает accounting. Универсальной команды rollback
нет; [ограничения восстановления](operations.md#доказательства-результата-и-замена-engine)
относятся и к повторному rebind после уже сохранённого перехода.
