# Native delivery

## Purpose

Define the portable delivery and project isolation contract for the current
ChangeRail runtime, preserving evidence and review accounting across continuations.
## Requirements
### Requirement: Native lifecycle
The runtime SHALL execute one openspec-v1 change per card and SHALL allow at most
two independent review cycles across ordinary delivery and repair.

#### Scenario: Repair accounting
- **WHEN** a run resumes or performs a semantic repair
- **THEN** previous independent reviews remain counted
- **AND** historical allowances do not create another review cycle

### Requirement: Recover a pre-group technical model failure
Runtime SHALL allow a single append-only technical recovery when a model session
fails before the next native task group starts, the failure is in the explicit
technical allowlist, payload and predecessor receipts are unchanged, and no writer,
review, final or publication intent is active.

#### Scenario: Capacity failure before next group
- **WHEN** completed groups and evidence exist but the next session exits with a
  recognized model capacity error before `change-N starting`
- **THEN** prepare/apply creates one successor linked by `recovery_of` and runs only
  the pending group with the fixed fallback model
- **AND** old run bytes, checkpoints, evidence, counters and review allowance remain unchanged

#### Scenario: Ambiguous or semantic failure
- **WHEN** the process may still be alive, failure is unknown, writer started, payload
  drifted, or the failure is a test/product/worker error
- **THEN** recovery is rejected before writer launch and no successor or allowance is created

#### Scenario: Repeat and concurrent apply
- **WHEN** the same receipt is applied again or two recoveries race
- **THEN** one attempt is retained; the same successor may be reconciled, while a
  second successor or changed model/payload is rejected

### Requirement: Separate project and tool ownership
The runtime SHALL keep project Git operations, profile, board and evidence in
the selected project while loading shared code from its declared tool source.

#### Scenario: Shared source
- **WHEN** two projects are attached to one source checkout
- **THEN** each observes the same shared code
- **AND** each retains its own profile, delivery lock and runtime artifacts

### Requirement: Explicit source change
The runtime SHALL retain the effective code identity for execution and SHALL
refuse ordinary continuation when the frozen identity changes.

#### Scenario: Repair continuation
- **WHEN** a stopped eligible run adopts a tested tool correction
- **THEN** a separate receipt records previous and new identity and regression evidence
- **AND** the original run metadata and consumed reviews remain unchanged

#### Scenario: Shared OpenSpec runtime drift
- **WHEN** an OpenSpec workflow loader, installation checker, package manifest,
  package lock, bootstrap or shared Python package initializer changes
- **THEN** ordinary continuation refuses the changed execution identity
- **AND** linked consumers enforce the same check without rewriting saved runs

### Requirement: Recover interrupted source attachment
The installer SHALL require ignored runtime storage before attaching shared
source and SHALL permit detachment from an unavailable source using checked
local backups without granting execution authority to broken links.

#### Scenario: Source moved after attachment
- **WHEN** the shared checkout is moved or removed and the attachment links and
  retained local backup are unchanged
- **THEN** detach restores the exact pre-attachment files
- **AND** normal runtime execution still rejects the unavailable source

#### Scenario: Attachment without ignored runtime storage
- **WHEN** attachment is requested without ignored runtime storage
- **THEN** the installer refuses before writing lock, backup or attachment files

### Requirement: Preserve archive intent through date rollover
The runtime SHALL preserve the initial archive intent while allowing its UTC
destination date to advance through linked receipts after revalidating the exact
payload, HEAD and absence of conflicting archive destinations.

#### Scenario: Stopped before stock archive
- **WHEN** a saved intent predates the current UTC date and the active change
  still matches its retained artifacts and surrounding payload
- **THEN** the runtime records a successor intent before invoking stock archive
- **AND** continuation preserves the original intent and successor chain

### Requirement: History remains read only
The runtime SHALL preserve historical adopted runs without granting new execution authority.

#### Scenario: Read old run
- **WHEN** status or metrics reads an adopted run
- **THEN** its saved files remain unchanged
- **AND** observation does not authorize resume or publication

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

### Requirement: Isolate self-host engine identity
Runtime SHALL execute self-host delivery from an immutable, hash-identified engine
snapshot separate from the mutable project checkout; drift of engine, launcher,
profile or binding SHALL block execution.

#### Scenario: Mutable project with pinned engine
- **WHEN** product runtime files change during self-host delivery while the pinned
  engine inventory remains unchanged
- **THEN** execution continues with the pinned engine and records separate engine and
  project identities

### Requirement: Recover self-host run into one successor
Runtime SHALL provide append-only prepare/apply/reconcile recovery that records the
complete predecessor inventory, accepted plan, corrective delta, engine identity and
review accounting, then atomically creates at most one successor.

#### Scenario: Finalize without replay
- **WHEN** a stopped self-host run has completed groups and no writer or review intent
- **THEN** one successor is created, history and accounting are retained, completed
  groups are not replayed, and the successor enters the normal finalize lifecycle.

#### Scenario: Drift, race or boundary violation
- **WHEN** engine/project inputs drift, a process is live, verification is unresolved,
  or review/final/archive/publication has begun
- **THEN** recovery fails closed without a second successor or new review allowance.

### Requirement: Continue a verified bound finalization
Runtime SHALL retain exact history and frozen project inputs while explicitly transitioning a terminal self-host finalization to a verified replacement engine.

#### Scenario: Explicit engine replacement
- **WHEN** the operator supplies a verified new snapshot and the exact previous engine identity while no delivery writer is live
- **THEN** an append-only before/after receipt and atomic binding replacement are reconciled idempotently without modifying predecessor runs or granting ordinary resume on changed identity.

#### Scenario: Empty exact payload
- **WHEN** an explicitly selected terminal self-host run has a clean payload exactly matching its retained manifest and execution identity
- **THEN** ordinary continuation preserves its completed groups and review accounting and executes the remaining lifecycle gates.

#### Scenario: Unsafe transition
- **WHEN** engine or project inputs drift, the requested previous identity differs, or another writer owns delivery
- **THEN** transition fails closed without a second binding decision or rewritten run evidence.

### Requirement: Recurrence analysis across review verdicts
Runtime SHALL строить для каждого завершённого NO-GO детерминированный разбор
истории review: какие findings повторяются, какие закрыты, какие появились
впервые, менялись ли затронутые условия и пути. Разбор MUST опираться только на
сохранённые verdicts, принятый план и карточку и MUST NOT изменять их. Разбор
MUST попадать в контекст следующего ремонта, чтобы ремонт видел историю, а не
только последний вердикт.

#### Scenario: Повторяющийся дефект
- **WHEN** finding второго NO-GO ссылается на то же условие и тот же путь, что и finding первого
- **THEN** разбор помечает его как повторяющийся и фиксирует, что предыдущий ремонт его не закрыл

#### Scenario: Закрытый дефект
- **WHEN** условие, проваленное в первом NO-GO, проходит во втором
- **THEN** разбор фиксирует закрытие и не предлагает повторный ремонт по нему

### Requirement: Bounded diagnosis before a terminal review stop
Runtime SHALL при исчерпании review остатка выполнять ограниченную стадию
диагностики вместо немедленного отказа. Диагностика SHALL разбирать все NO-GO
линии, принятый план и критерии карточки и SHALL определять класс ситуации из
закрытого набора: повторяющийся дефект, неполнота работы, конфликт принятого
плана и требований ревью, пробел модели доказательств, невоспроизводимое
наблюдение, инфраструктурный блокер, невыполнимый критерий. Если сохранённая
история не позволяет установить класс, диагностика MUST NOT угадывать: решение
остаётся за оператором. Диагностика MUST
быть идемпотентной и привязанной к точной истории: повтор при неизменном
состоянии MUST NOT создавать второй разбор.

#### Scenario: Один разбор на исчерпание
- **WHEN** диагностика уже выполнена для точного состояния линии
- **THEN** повторный запуск возвращает сохранённый разбор и не запускает новую сессию

#### Scenario: Изменившееся состояние
- **WHEN** история, план или payload изменились после разбора
- **THEN** прежний разбор помечается неприменимым и не используется как основание решения

#### Scenario: Класс не установлен
- **WHEN** детерминированный разбор не устанавливает класс по сохранённой истории
- **THEN** runtime MUST NOT угадывать класс, а предъявляет оператору полный набор поддержанных переходов

### Requirement: Diagnosis grants no authority
Диагностика MUST NOT расходовать review, выдавать слот, изменять Acceptance или
scope, ослаблять гейты, продолжать доставку, публиковать или объявлять доставку
успешной. Worker MUST NOT использовать разбор как полномочие. Классификация,
предложенная диагностикой, MUST проверяться runtime по сохранённому состоянию, а
не приниматься на веру.

#### Scenario: Разбор не даёт права на ревью
- **WHEN** диагностика предлагает системный ремонт, но слот не выдан
- **THEN** writer не запускается, доставка не продолжается, разбор остаётся предложением

#### Scenario: Диагностика не меняет критерии
- **WHEN** диагностика считает критерий невыполнимым
- **THEN** критерий и принятый план остаются неизменными до явного решения оператора

### Requirement: Operator choice after an exhausted diagnosis
Runtime SHALL предъявлять оператору структурированный выбор, когда системный
путь внутри принятого scope не найден: варианты с ожидаемым эффектом, ценой
(ревью, scope, архитектура), предусловиями и рекомендацией. Остановка MUST быть
штатным состоянием, а не ошибкой, и MUST сохранять историю, accounting и
frozen identity. Выбор оператора SHALL фиксироваться отдельной неизменяемой
записью, связанной с точным разбором и состоянием линии.

#### Scenario: Несколько решений
- **WHEN** существует несколько путей с разной ценой
- **THEN** оператор получает варианты с обоснованием и выбирает один; автоматический выбор не производится

#### Scenario: Инфраструктурный блокер
- **WHEN** причина не является продуктовым дефектом
- **THEN** диагноз сообщает средовую причину и не предлагает маршрут, который не может выполниться: существующее техническое восстановление принимает только исходный остановленный run до первого ревью, поэтому оператору предлагаются выполнимые маршруты, а не ещё одно ревью

#### Scenario: Неизменность при остановке
- **WHEN** доставка остановлена в ожидании решения
- **THEN** старые runs, verdicts, receipts и evidence сохраняются побайтно, а счётчики review не сбрасываются

### Requirement: Criterion amendment is a separate operator decision
Runtime SHALL принимать изменение формулировки критерия только как отдельное
явное решение оператора, когда диагностика установила, что критерий невыполним
в текущей формулировке или требуемое доказательство невыразимо. Запись MUST
связывать прежнюю и новую формулировку, обоснование, автора, точный разбор и
состояние линии. Исходная формулировка MUST сохраняться как история. Изменение
критерия MUST NOT выдавать слот, отменять собранные proofs, объявлять прежние
NO-GO недействительными или делать доставку успешной; после него требуется
обычное независимое ревью на текущий payload.

#### Scenario: Амендмент критерия
- **WHEN** оператор меняет формулировку критерия на основании разбора
- **THEN** прежняя формулировка остаётся в истории, запись связывает оператора и время, слот не появляется
- **AND** новая формулировка применяется к карточке и принятому плану отдельным обычным маршрутом принятия, а не самим амендментом; до этого доставка не продолжается

#### Scenario: Амендмент не отменяет гейты
- **WHEN** критерий изменён
- **THEN** proofs, handoff, archive, final verification и publication остаются обязательными, а прежние вердикты сохраняются

#### Scenario: Чужой или устаревший амендмент
- **WHEN** запись ссылается на другой run, устаревший разбор или изменённое состояние линии
- **THEN** она отклоняется до применения

### Requirement: Continuation after the chosen option
После решения оператора работа SHALL продолжаться по той же карточке. Для
системного ремонта внутри принятого scope SHALL использоваться обычный маршрут
ремонта и независимого ревью с существующим учётом слотов. Для пересмотра плана
или архитектуры SHALL закрываться текущая попытка и приниматься отдельный новый
план; закрытие MUST NOT объявлять доставку успешной и MUST NOT обнулять
accounting исходной линии. Автоматическое продолжение без решения оператора
MUST NOT происходить. Если записанный переход требует отдельного маршрута
(закрытие попытки, пересмотр плана, изменение критерия, техническое
восстановление), runtime MUST NOT выполнять вместо него обычный ремонт: он
останавливается и называет этот маршрут.

#### Scenario: Системный ремонт внутри scope
- **WHEN** оператор выбрал системный ремонт, и слот доступен
- **THEN** ремонт идёт по обычному маршруту, а ревью требует независимого вердикта на текущий payload

#### Scenario: Пересмотр плана
- **WHEN** оператор выбрал пересмотр плана или архитектуры
- **THEN** текущая попытка закрывается как неуспешная, исходная история сохраняется, а новый план принимается отдельно

#### Scenario: Недопустимый выбор
- **WHEN** выбранный вариант противоречит поддержанным переходам, границам публикации или сохранённой истории
- **THEN** выбор отклоняется до запуска writer, состояние не изменяется

