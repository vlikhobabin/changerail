## ADDED Requirements

### Requirement: Explicit unsuccessful closure of exhausted native delivery
Runtime SHALL предоставлять подготовку и явное применение неуспешного закрытия
последнего остановленного native run, когда allowance lineage исчерпан
(`remaining = 0` по общему расчёту `2 + operator_granted_slots - spent_reviews`)
и последний завершённый verdict равен NO-GO. Закрытие MUST работать и для
lineage, исчерпавшей только автономные два review, и для lineage, исчерпавшей
дополнительные операторские слоты. Worker session MUST NOT применять закрытие.
Закрытие MUST NOT выполнять review, archive, commit или push и MUST NOT
возвращать, переиспользовать или обнулять выданные слоты и расход review.

#### Scenario: Подготовка и применение
- **WHEN** внешний оператор подтверждает digest актуального предложения закрытия исчерпанной остановленной lineage
- **THEN** карточка переходит из 3.inprogress в 5.canceled с явно неуспешным результатом
- **AND** frozen sections сохранены, новый GO и успешный archive не создаются

#### Scenario: Неподдержанное состояние
- **WHEN** найден живой writer, чужая identity, новый descendant, незавершённый review/verification, конкурирующий recovery, archive/final/publication intent либо бюджет не исчерпан
- **THEN** операция отклоняется до изменения доски и не запускает сессии

### Requirement: Restorable payload and immutable closure history
Runtime MUST сохранять полный восстанавливаемый текущий payload отдельно от
последнего reviewed payload и побайтно сохранять прежние runs, receipts,
manifests, verdicts и evidence. Применение SHALL проверять согласованный snapshot
и фиксировать закрытие отдельной записью с прежним расходом review.

#### Scenario: Новый ремонт после NO-GO
- **WHEN** payload содержит tracked изменения, новый бинарный файл, удаление, режим executable и symlink после последнего review
- **THEN** snapshot восстанавливает все эти изменения без разыменования ссылок
- **AND** reviewed/current fingerprints различимы, старый verdict не объявляет новый ремонт проверенным

#### Scenario: Stale proposal или непустой index
- **WHEN** HEAD, payload либо подготовленная история изменились перед apply, или index непуст
- **THEN** операция отклоняется, пользовательские изменения и index сохраняются

#### Scenario: Прерывание и повтор
- **WHEN** apply прерван после intent либо посреди перемещения карточки/обновления допустимых ссылок
- **THEN** новая доставка блокируется до завершения того же intent
- **AND** повтор завершает один переход или сообщает конфликт без перезаписи посторонних изменений

### Requirement: Terminal closure without inherited execution authority
Runtime MUST запрещать исполнение закрытой lineage через все delivery/recovery
entrypoints, включая её предков. Status SHALL показывать терминальное закрытие;
завершённое закрытие SHALL освобождать активное место на доске. Создание связанного
плана MUST NOT принимать его автоматически или сбрасывать расход старой lineage.

#### Scenario: Попытка продолжения закрытой истории
- **WHEN** запрошены resume, run recovery, handoff, review, restoration либо publish закрытого run или его предка
- **THEN** вызов отклоняется до writer, прежний расход review и выданные слоты сохраняются без изменений

#### Scenario: Новый план после закрытия
- **WHEN** оператор создаёт связанную backlog-карточку перепроектирования
- **THEN** она остаётся непринятой до отдельного native acceptance
- **AND** старое evidence не становится её доказательством, dirty payload остаётся сохранённым и явно указанным

### Requirement: Terminal-only compatibility for installed rc3 history
Проверенный новый инструмент SHALL закрывать доказанную native историю
installed 2.0.0-rc.3 через явный project path без замены installed runtime.
Поддержка чтения для закрытия MUST NOT расширять совместимость исполнения,
plan restoration, checkpoint inheritance или review allowance.

#### Scenario: Внешний комплект и старый installed проект
- **WHEN** CLI нового комплекта получает явный project с проверенным rc.3 lock/inventory и исчерпанной lineage
- **THEN** prepare/apply завершают её неуспешно без изменения installed runtime, lock, launcher и profile
- **AND** старые runs сохраняются, их resume остаётся запрещён

#### Scenario: История только для чтения и неизвестное происхождение
- **WHEN** предъявлена retained read-only native история с доказанным rc.3 происхождением
- **THEN** допускается только terminal closure, без effective execution identity
- **AND** неизвестная версия, подменённое происхождение или неподдержанная стадия отклоняются
