## ADDED Requirements

### Requirement: Restore only the accepted Next bytes
Runtime SHALL готовить восстановление Next stopped native run из доказанного
accepted source, возвращая ровно исходный byte span и сохраняя остальные байты.
Runtime MUST проверить полный accepted identity и исходный exact payload до записи.

#### Scenario: Подготовка точного восстановления
- **WHEN** Next изменён, остальные frozen sections и normalized artifacts совпадают, а payload совпадает с последним manifest
- **THEN** prepare показывает accepted source, before/after hashes и точный diff
- **AND** dry-run не меняет ни карточку, ни историю, ни runtime receipts

#### Scenario: Чужая правка или недостоверный источник
- **WHEN** Scope, Acceptance, artifacts, profile, launcher, product payload либо источник исходного Next не проходит проверку
- **THEN** prepare/apply отказывает до изменения payload или установки runtime

### Requirement: Append-only restoration transaction
Runtime SHALL сохранять proposal, durable intent, applied и consumption receipts
отдельно от всех исходных runs, с полномочием на точный proposal hash и связью
с каждым predecessor. Старые файлы и состав каталогов runs MUST оставаться неизменными.

#### Scenario: Применение и продолжение
- **WHEN** явно одобренный proposal повторно проверен под project lock
- **THEN** apply записывает intent, атомарно восстанавливает карточку и сохраняет effective manifest отдельного перехода
- **AND** новый run ссылается на transition и последнюю recovery попытку без пересэмплирования старого manifest

#### Scenario: Повтор, writer и прерывание
- **WHEN** apply повторён, конкурирует с writer, получает drift после prepare либо прерывается между intent и applied
- **THEN** runtime исключает двойное применение и запись при drift/concurrent writer
- **AND** reconcile дописывает квитанцию только для доказанного before/after состояния; обычное продолжение блокируется до завершения intent

### Requirement: Preserve failed recovery ancestry
Runtime SHALL разрешать отсутствие native-plan у failed pre-import child только
при доказанном accepted origin в полной неизменной ancestry того же card/change.
Runtime MUST NOT дописывать отсутствующий план в исторический child.

#### Scenario: Предшественник не успел импортировать план
- **WHEN** последняя попытка имеет exact manifest и остановилась до import_accepted
- **THEN** transition фиксирует accepted-plan origin из проверенного предка и копирует план только в successor
- **AND** child остаётся частью цепочки попыток и review accounting

#### Scenario: Разрыв или подмена ancestry
- **WHEN** происхождение плана неоднозначно, предок отсутствует, history hashes изменены либо выбран другой predecessor
- **THEN** prepare, apply и resume отклоняют переход

### Requirement: Refresh proofs without resetting delivery accounting
Runtime SHALL сохранять complete checkpoints только при неизменной семантике
задач и проверенных событиях, инвалидировать устаревшие proofs и получать новые
evidence до handoff и продвижения. Runtime MUST сохранять общий лимит двух review.

#### Scenario: Продолжение после завершённых групп
- **WHEN** Next восстановлен и semantic task identity не изменена
- **THEN** successor не повторяет complete events, обновляет необходимые focused/observed proofs и проходит оставшиеся finalize, sync, review, archive, final и publication gates
- **AND** старые evidence и GO не объявляются текущими receipts

#### Scenario: Расход ревью
- **WHEN** lineage уже потратила один либо два независимых review
- **THEN** допустимый остаток равен одному либо нулю; новый переход не создаёт дополнительной попытки

#### Scenario: Несвязанный блокер проекта
- **WHEN** восстановленный run достигает проверки с dangling board reference либо другой независимой ошибкой
- **THEN** runner сохраняет отказ и не ослабляет gate ради завершения восстановления

### Requirement: Explicit installed runtime compatibility
Runtime SHALL поддерживать установленный predecessor только через проверенную
совместимость execution schemas, frozen distribution provenance и отдельную
квитанцию старой/новой identity. Обычная установка MUST NOT давать право resume.

#### Scenario: Проверенный installed predecessor
- **WHEN** старый installed run с checkpoint/evidence и failed pre-import child имеет полные доказательства старого archive/lock и допускается compatibility descriptor
- **THEN** согласованный runtime transition устанавливает точный target и restoration возвращает управление штатному successor runner
- **AND** старые process identities и вся история остаются неизменными, новый run использует полную target identity

#### Scenario: Недостаточное доказательство совместимости
- **WHEN** старый identity map неполон без frozen lock, archive подменён, profile/launcher изменены либо schema неизвестна
- **THEN** runtime отказывает без автоматического дополнения старой identity

#### Scenario: Read-only история и неподдерживаемые стадии
- **WHEN** run помечен историческим read-only, остановлен оператором, имеет незавершённую verification attempt, archive intent, pending provisional review, final floor либо publication
- **THEN** restoration отклоняется и не предоставляет новых полномочий этому run

### Requirement: Explicit card state editing guidance
Native implementing skill SHALL разрешать только task checkbox progress и
обновление Result/Log по своей стадии, явно запрещать изменение frozen Next
и требовать успешный handoff до сообщения о завершении aggregate delivery.

#### Scenario: Handoff отвергнут
- **WHEN** implementing session получает ненулевой exit handoff
- **THEN** она сообщает конкретный blocker, сохраняет run и не заявляет успешную передачу runner
