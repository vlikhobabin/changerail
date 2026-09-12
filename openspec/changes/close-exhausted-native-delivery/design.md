## Context

Native runner ограничивает автономную часть lineage двумя независимыми review
и допускает операторские слоты при исчерпании остатка. Терминальный
NO-GO оставляет карточку в `3.inprogress`; `status` может показывать последнее
событие ожидания review. Поэтому основание закрытия определяется по завершённым
verdict и ancestry, а не по тексту последнего события. Текущий payload может
содержать последующий ремонт, к которому старый verdict не относится.

## Goals / Non-Goals

**Goals:** явное неуспешное закрытие точной остановленной lineage, сохранение
восстанавливаемого payload и старой истории, освобождение активной колонки,
применимость к installed rc.3 без права продолжения старого run.

**Non-Goals:** третье review, автоматический преемник, универсальный recovery,
публикация NO-GO, изменение installed core на месте, очистка чужого worktree.

## Decisions

### 1. Два явных действия с одним результатом

Новый модуль `scripts/changerail/native_closure.py` обслуживает
`native-close-prepare <run> --reason <text>` и
`native-close-apply <proposal> --authorize <sha256>`.
Prepare показывает точный proposed result и сохраняет локальный снимок.
Apply выполняется внешним операторским runner вне implementing/review session;
digest связывает поручение с конкретным предложением, а не выдаёт полномочия
самому worker. Существующий project lock и проверка отсутствия живых writers
применяются в обоих действиях. Общий framework транзакций не добавляется.

Обычный resume не подходит: закрытие не исполняет checkpoint и не расходует
новое review. `finalize_card` не подходит: он оформляет успешную доставку.

### 2. Проверить ровно основание закрытия

Поддерживается последний остановленный native run одной доказанной lineage
с исчерпанным allowance (`remaining = 0`) и последним завершённым NO-GO.
Расход считается общим расчётом `2 + operator_granted_slots - spent_reviews`,
поэтому закрытие одинаково работает для lineage с двумя автономными review и
для lineage, дополнительно исчерпавшей операторские слоты; выданные слоты и
прежний расход при закрытии не возвращаются и не обнуляются.
Использовать существующий расчёт ancestry/accounting, проверив card/change,
отсутствие более нового потомка, pending review, конкурирующего recovery intent,
archive/final/publication intent и незавершённой verification attempt.
Чужая identity, worker role и неоднозначная история отклоняются без изменения
доски. Непустой index отклоняется и остаётся нетронутым; staging не отменяется.

Proposal связывает project identity, HEAD, card/lineage, историю по hash,
последний reviewed fingerprint и отдельный current unreviewed fingerprint.
Старый verdict не проверяется как verdict текущего ремонта и не становится GO.
Snapshot содержит binary tracked diff, untracked bytes и manifest с удалениями,
типами, режимами и symlink targets без разыменования. Проверка восстановления
обязательна. Локальные секреты/логи не копируются в публичные fixtures или отчёт.

### 3. Сохранить завершение отдельно от исходной истории

Под `.runtime/changerail/closures/` записываются immutable proposal, intent
и completion receipt; каталоги исходных runs/receipts остаются побайтно прежними.
Перед intent apply повторно проверяет HEAD, payload и prepared inventory.
Intent сохраняет before/after bytes карточки и допустимых живых ссылок.
У карточки меняются только `Status`, `Result`, `Log`; `Next`, `Scope`,
`Acceptance` и остальные frozen sections сохраняются. Назначение — `5.canceled`,
результат явно неуспешен; OpenSpec change не архивируется как успешный.
Исторические и frozen ссылки не переписываются. Если нужная правка живой ссылки
затронула бы frozen план другой активной доставки, prepare сообщает конфликт.

Каждая запись делается атомарно; повтор того же apply завершает собственный
intent или возвращает прежний completion receipt. Конфликт с посторонней
правкой останавливает reconcile без её перезаписи. Незавершённый intent
блокирует начало новой доставки. Все execution/recovery entrypoints проверяют
closure по lineage, включая предков; status показывает закрытие рядом с историей.

### 4. Совместимость закрытия отдельно от совместимости исполнения

Основной путь для copy-install rc.3: оператор запускает **проверенный новый
комплект** из отдельного каталога с явным `--project`; операция читает старую
историю и меняет только результат закрытия/доску. Установка поверх проекта
и изменение его lock/launcher/profile не требуются. Нужен terminal-only decoder
поддержанного rc.3 schema/provenance с проверкой distribution lock/inventory;
неизвестные форматы/подменённые файлы отклоняются. В тестах фиксируются публичные
rc.3 wire fixtures/provenance, без реальных журналов потребителя и без загрузки
зависимостей по сети во время тестов.

Не расширять `installed_compatibility.REVIEWED_PAYLOADS`, effective execution
identity или права `plan-restore`/`require_current_execution`. Read-only history
с доказанным rc.3 происхождением может быть закрыта, но не запущена.
Простой upgrade не закрывает карточку и не разрешает resume. Путь из внешнего
комплекта проверяется subprocess CLI тестом, включая фактическую маршрутизацию
`--project`, а не только unit вызовом decoder.

### 5. Отдельный новый план

Закрытие освобождает активное место, но не принимает новую карточку и не очищает
рабочий payload. Runbook указывает оставшиеся dirty paths и сохранённый snapshot.
Перед следующей доставкой оператор отдельно готовит чистую базу, сохраняя
посторонние правки; выбранные части ремонта переносит implementing session
по новому принятому scope. Нет `reset --hard`, автоматического удаления
untracked файлов или скрытого нового бюджета старой lineage. Связанная backlog
карточка фиксирует причину перепроектирования и старую историю; её admission
является отдельным действием. Новый план не получает старый GO/evidence.

## Risks / Trade-offs

- Частичное перемещение карточки → retained intent, repeat того же apply,
  fail-closed execution gates до completion; fault injection в регрессиях.
- Неполный backup → round-trip с binary, deletion, executable mode и symlink.
- Признание ремонта проверенным → reviewed/current identity хранятся раздельно.
- Допуск старого runtime к исполнению → отдельный terminal-only decoder;
  отрицательные проверки resume/restoration обязательны.
- Dirty payload остаётся после закрытия → явное сообщение и отдельная подготовка
  базы; это намеренное сохранение работы, а не обещание немедленного `run`.

## Migration Plan

Доставить изменение инструмента через независимый review. Проверить новый
комплект на synthetic copy-install rc.3. Затем prepare реального потребителя,
проверить proposal/snapshot и применить по поручению оператора. Closure terminal:
автоматический rollback не предоставляется; прерванный apply завершается тем же
proposal. При конфликте сохраняется intent и выдаётся точное расхождение.
Публикация версии инструмента — отдельная операция внешнего runner.

## Open Questions

Открытых продуктовых решений нет. Формат wire record и расположение коротких
CLI hooks уточняются реализацией в пределах этого контракта.
