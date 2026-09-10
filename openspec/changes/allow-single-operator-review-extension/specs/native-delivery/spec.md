## MODIFIED Requirements

### Requirement: Native lifecycle
Runtime SHALL исполнять один openspec-v1 change на карточку и по умолчанию
допускать максимум два независимых review на всю delivery lineage. Единственное
доверенное операторское исключение SHALL разрешать один дополнительный repair
и review; абсолютный предел SHALL равняться трём. Profile `max_review_cycles`
MUST оставаться равным 2 и MUST NOT служить источником исключения.

#### Scenario: Repair accounting
- **WHEN** run продолжается или выполняет semantic repair
- **THEN** предыдущие независимые reviews остаются учтёнными
- **AND** исторические allowances, новый child и восстановление сами по себе не создают ещё один review

#### Scenario: Default stop after two reviews
- **WHEN** два reviews завершены, последний имеет валидный NO-GO и доверенного исключения нет
- **THEN** writer/repair/review не запускаются, runtime сообщает исчерпание обычного бюджета
- **AND** оператор может просмотреть предложение ограниченного исключения

### Requirement: Refresh proofs without resetting delivery accounting
Runtime SHALL сохранять complete checkpoints только при неизменной семантике
задач и проверенных событиях, инвалидировать устаревшие proofs и получать новые
evidence до handoff и продвижения. Runtime MUST сохранять общий учёт review:
default 2, отдельное однократное operator +1 и абсолютный предел 3.
Plan restoration MUST NOT самостоятельно выдавать исключение или расширять
свою допустимую область восстановления.

#### Scenario: Продолжение после завершённых групп
- **WHEN** Next восстановлен и semantic task identity не изменена
- **THEN** successor не повторяет complete events, обновляет необходимые focused/observed proofs и проходит оставшиеся finalize, sync, review, archive, final и publication gates
- **AND** старые evidence и GO не объявляются текущими receipts

#### Scenario: Расход ревью
- **WHEN** lineage уже потратила один либо два независимых review без отдельного operator grant
- **THEN** допустимый остаток равен одному либо нулю; новый переход не создаёт дополнительной попытки

#### Scenario: Несвязанный блокер проекта
- **WHEN** восстановленный run достигает проверки с dangling board reference либо другой независимой ошибкой
- **THEN** runner сохраняет отказ и не ослабляет gate ради завершения восстановления

#### Scenario: Исключение не расширяет restoration
- **WHEN** lineage имеет grant дополнительного review, но plan restoration не допускает её стадию
- **THEN** restoration отклоняется, grant и review accounting сохраняются без пополнения

## ADDED Requirements

### Requirement: Explicit operator authority outside worker control
Runtime SHALL принимать исключение только от аутентифицированного оператора
через защищённую от worker границу authority. Worker MAY подготовить предложение,
но MUST NOT одобрять его, изменять trust configuration или authoritative ledger.
Runtime SHALL сохранять default 2 при отсутствии доказанной границы доверия.

#### Scenario: Worker attempts self authorization
- **WHEN** worker создаёт approved JSON, подставляет SHA, TTY, env flag, local endpoint или вызывает operator API
- **THEN** authority отклоняется до writer launch, дополнительный grant не появляется

#### Scenario: Separate operator approves exact proposal
- **WHEN** зарегистрированный operator principal явно одобряет просмотренный точный proposal через защищённый endpoint
- **THEN** issuer создаёт immutable receipt с operator identity, reason, project/root binding и объёмом one repair plus one review
- **AND** разрешение не выдаёт commit/push либо platform runtime authority

#### Scenario: Same UID or writable authority contour
- **WHEN** worker может действовать от имени оператора/coordinator либо писать executable/config/state доверенной стороны
- **THEN** исключение недоступно с диагностикой authority-unavailable, ordinary delivery сохраняет default 2

### Requirement: Bounded proposal for the final NO-GO
Runtime SHALL готовить proposal только для доказанной native lineage с ровно
двумя завершёнными reviews и последним валидным NO-GO. Proposal MUST связывать
exact predecessor, ancestry, HEAD/payload, frozen identities, unchanged accepted
plan/Scope/Acceptance, findings, причину неполного repair, разрешённые изменения
и план регрессий/evidence. Dry-run MUST NOT изменять состояние доставки.

#### Scenario: Ready final repair proposal
- **WHEN** eligible run и конкретный repair plan проходят проверки
- **THEN** prepare показывает bindings, findings, ограниченный scope, доказательства и terminal outcome третьей неудачи
- **AND** сохранённый proposal сам по себе не запускает repair

#### Scenario: Stale foreign or unsupported proposal
- **WHEN** proposal чужой, устарел, расширяет Acceptance/scope, имеет неизвестную ancestry либо есть unfinished review/verification или archive/final/publication intent
- **THEN** prepare/apply отклоняются до изменения старых runs, runtime installation или writer launch

### Requirement: Single protected lineage reservation
Runtime SHALL иметь единственный authoritative grant и attempt reservation на
registered project/root delivery. Все review, semantic repair, final-floor
repair, recovery и installed transition MUST использовать общий расчёт allowance.
Reservation MUST происходить до дополнительного repair writer и MUST NOT
возвращаться в пул после crash, cancel или infrastructure failure.

#### Scenario: Rename child reinstall or local rollback
- **WHEN** delivery переименована, получает child, другой runtime либо replay локальных receipts
- **THEN** registry сохраняет прежнюю root identity, grant и расход
- **AND** четвёртый review, второй grant и автоматическая replacement delivery отклоняются

#### Scenario: Concurrent reserve and interrupted successor
- **WHEN** конкурируют resume либо процесс прервался между reserve, staging и successor publication
- **THEN** только один attempt и один writer lease разрешены
- **AND** reconcile продолжает тот же attempt только из доказанного состояния без изменения predecessor files или состава старых run directories

#### Scenario: Missing authoritative evidence
- **WHEN** broker недоступен, lineage history исчезла или local revision противоречит authoritative ledger
- **THEN** extension lineage блокируется без fallback к ordinary allowance

### Requirement: Finding-bound final repair and review
Runtime SHALL перед review №3 требовать для каждого разрешённого finding
воспроизведение, причину, исправление всего затронутого пути, регрессию и fresh
evidence. GO №3 MUST проходить прежние archive/final/publication gates.
NO-GO №3 или необходимость нового semantic/product repair после него MUST
переводить delivery в terminal exhausted.

#### Scenario: Third GO with complete evidence
- **WHEN** repair остаётся в разрешённом scope и review №3 выдаёт валидный GO на текущий payload
- **THEN** runner выполняет обычные оставшиеся gates с актуальными fingerprints
- **AND** публикация требует прежнего отдельного полномочия и успешного final floor

#### Scenario: Third NO-GO or new final repair
- **WHEN** review №3 выдаёт NO-GO либо после него требуется новое существенное исправление
- **THEN** состояние exhausted терминально, новое предложение исключения и review №4 запрещены

#### Scenario: Archive evidence refresh
- **WHEN** stock archive требует обновления evidence при неизменном продукте
- **THEN** runner обновляет предусмотренные proofs без скрытого semantic repair или новой независимой review session

### Requirement: Explicit pause cancel and finite infrastructure continuation
Runtime SHALL проверять operator pause/cancel перед следующим writer/stage,
сохранять grant/attempt и фактические effects уже запущенной операции.
Canceled и exhausted MUST быть терминальными для delivery. Extension attempt
SHALL иметь максимум одно автоматическое infrastructure continuation на все
стадии вместе, с прежними attempt/session/check identity и резервированием.

#### Scenario: Pause and explicit unpause
- **WHEN** оператор приостанавливает нетерминальный attempt
- **THEN** следующий переход не запускается автоматически
- **AND** только явный unpause и допустимый resume продолжают прежнюю стадию с тем же остатком; budget и infrastructure block не сбрасываются

#### Scenario: Cancellation
- **WHEN** оператор отменяет нетерминальную delivery
- **THEN** дальнейшие writers запрещены, уже выполненные effects и reservation сохраняются

#### Scenario: Provable first technical continuation
- **WHEN** первый технический сбой оставил завершённый процесс и доказанную возможность продолжить ту же session/check без нового review
- **THEN** continuation использует прежний attempt и расходует единственный technical recovery allowance
- **AND** технический сбой не становится NO-GO

#### Scenario: Repeated or ambiguous infrastructure failure
- **WHEN** повторился технический сбой, отсутствует session identity, результат launch неизвестен либо старый процесс ещё жив
- **THEN** runtime сообщает infrastructure-blocked без автоматического retry
- **AND** повторный CLI, новый child и pause/unpause не пополняют budget; assertion failure не классифицируется как инфраструктура

### Requirement: Explicit installed review extension transition
Runtime SHALL поддерживать установленный predecessor с двумя NO-GO только через
отдельный проверенный compatibility descriptor и operator grant, связывающий
точные old/target identities, архив и защищённый execution contour. Первый
набор SHALL покрывать точные известные rc.2 и rc.3 payload. Обычный install,
runtime-repair и plan restoration MUST NOT предоставлять это исключение.

#### Scenario: Known installed predecessor and exact archive
- **WHEN** проверенный новый coordinator принимает eligible rc.2/rc.3 predecessor с полным frozen lock, неизменным профилем/launcher и одобренным target contour
- **THEN** отдельный apply устанавливает точный архив и готовит successor через тот же grant/attempt
- **AND** оригинальная ancestry побайтно сохраняется, свежие evidence и review №3 проходят штатно

#### Scenario: Unsupported migration or pending transaction
- **WHEN** payload неизвестен, history read-only, predecessor остановлен оператором, frozen binding изменён или transition intent незавершён
- **THEN** обычные writers/installers отклоняются; незавершённый intent допускает только проверенное reconcile того же apply
- **AND** установка и миграция не создают grant, новый бюджет или исполнительное право историческому run
