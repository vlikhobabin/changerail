## MODIFIED Requirements

### Requirement: Native lifecycle
Runtime SHALL исполнять один openspec-v1 change на карточку и SHALL допускать
два автономных независимых review на всю delivery lineage. Каждое последующее
независимое review SHALL требовать отдельного явного решения оператора при
исчерпанном остатке. Profile `max_review_cycles` MUST оставаться строго равным 2
и MUST NOT служить источником дополнительного слота. Пожизненного абсолютного
предела числа review SHALL NOT вводиться.

#### Scenario: Repair accounting
- **WHEN** run продолжается или выполняет semantic repair
- **THEN** предыдущие независимые reviews остаются учтёнными
- **AND** исторические allowances, новый child, resume и установка runtime сами по себе не создают ещё один review

#### Scenario: Default stop after two autonomous reviews
- **WHEN** два автономных review завершены, последний имеет валидный NO-GO и операторского разрешения нет
- **THEN** writer, repair и review не запускаются, runtime сообщает исчерпание общего остатка и необходимость `review-allow`
- **AND** оператор может получить preview ограниченного разрешения

#### Scenario: Later review at exhaustion
- **WHEN** остаток исчерпан, lineage терминально остановлена и оператор выдал ровно один слот
- **THEN** допустимо одно дополнительное независимое review с прежними proofs, scope и финальными гейтами
- **AND** после исчерпания нового слота следующее review снова требует отдельного решения оператора

### Requirement: Refresh proofs without resetting delivery accounting
Runtime SHALL сохранять complete checkpoints только при неизменной семантике
задач и проверенных событиях, инвалидировать устаревшие proofs и получать новые
evidence до handoff и продвижения. Runtime MUST сохранять общий учёт review:
`remaining = 2 + operator_granted_slots - spent_reviews`. Plan restoration, self-host
recovery, runtime repair и установка runtime MUST NOT самостоятельно выдавать
дополнительный слот и MUST NOT расширять свою допустимую область восстановления.

#### Scenario: Продолжение после завершённых групп
- **WHEN** Next восстановлен и semantic task identity не изменена
- **THEN** successor не повторяет complete events, обновляет необходимые focused/observed proofs и проходит оставшиеся finalize, sync, review, archive, final и publication gates
- **AND** старые evidence и GO не объявляются текущими receipts

#### Scenario: Расход ревью
- **WHEN** lineage потратила часть независимых review
- **THEN** допустимый остаток учитывает выданные и провёденные слоты и не сбрасывается новым child, resume или установкой runtime

#### Scenario: Несвязанный блокер проекта
- **WHEN** восстановленный run достигает проверки с dangling board reference либо другой независимой ошибкой
- **THEN** runner сохраняет отказ и не ослабляет gate ради завершения восстановления

#### Scenario: Слот не расширяет restoration
- **WHEN** lineage имеет выданный слот, но plan restoration не допускает её стадию
- **THEN** restoration отклоняется, слот и review accounting сохраняются без пополнения

## ADDED Requirements

### Requirement: Cooperative operator review authorization
Runtime SHALL принимать дополнительный слот только как отдельное явное решение
оператора, полученное вне worker-контекста. Протокол SHALL быть кооперативным в
пределах одного UID и MUST NOT заявлять аутентификацию оператора средствами ОС.
Разрешение SHALL выдаваться двухфазно: preview возвращает digest проверенного
запроса, а `--authorize` с этим digest атомарно добавляет неизменяемую запись
вне старых run directories. Повтор того же подтверждения MUST NOT добавлять
второй слот. Разрешение MUST NOT менять старые verdicts, runs, receipts,
profile, frozen identity, принятый scope или proofs.

#### Scenario: Preview does not grant
- **WHEN** оператор выполняет preview для точного остановленного run
- **THEN** возвращается digest и полное предложение, но ни один слот не появляется
- **AND** состояние доставки не изменяется

#### Scenario: Authorize appends one immutable record
- **WHEN** оператор передаёт digest, совпадающий с текущим проверенным состоянием
- **THEN** под блокировкой проекта добавляется ровно одна неизменяемая запись разрешения
- **AND** устаревший или подменённый digest отклоняется без записи

#### Scenario: Worker attempts self authorization
- **WHEN** worker вызывает CLI или callable API из session/native/recovery контекста, подставляет digest, правит локальный JSON или очищает переменные окружения
- **THEN** разрешение отклоняется до появления слота
- **AND** обычная доставка сохраняет автономный остаток двух review

#### Scenario: Repeat, race and lost response
- **WHEN** подтверждение повторено, два оператора конкурируют или ответ authorize потерян
- **THEN** публикуется не более одного слота, а повтор возвращает уже опубликованную запись
- **AND** история и accounting остаются неизменными

### Requirement: Review slot binding through supported recovery
Выданный слот SHALL связываться с единственным детерминированным recovery
successor до появления writer и MUST NOT допускать второго child или второго
независимого reviewer. Проведение слота SHALL сохранять lineage review ordinal,
общий для provisional и final продолжения одного reviewer thread. Незавершённый
claim, чужой проект, изменённый начальный payload, незавершённые
review/verification и конфликтующий recovery intent MUST блокировать выдачу и
проведение слота. Незавершённое review занимает слот и недоступно другому запуску.

#### Scenario: Grant binds one successor before writer
- **WHEN** выданный слот проводится через поддерживаемый recovery
- **THEN** ссылка на разрешение записывается в первоначальный recovery context до dispatch
- **AND** повторный или параллельный запуск не создаёт второго child

#### Scenario: Partial or ambiguous claim
- **WHEN** процесс прервался между claim, dispatch и появлением successor
- **THEN** повторный слот не выдаётся, разбор идёт по сохранённому child
- **AND** удаление context ради повторного запуска не является поддерживаемым путём

#### Scenario: Grant does not weaken gates
- **WHEN** слот выдан и repair выполнен
- **THEN** свежие proofs, handoff, sync, archive, final verification и publication gates обязательны
- **AND** разрешение не выдаёт commit, push, платформенное или продуктовое полномочие

#### Scenario: Read-only history grants nothing
- **WHEN** run помечен как retained read-only установленной историей
- **THEN** статус сообщает read-only и исполнение, слот и resume отклоняются
