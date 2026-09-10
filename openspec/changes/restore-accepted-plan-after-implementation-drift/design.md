## Context

`_card_contract()` исключает Status/Result/Log, но включает Next. Native admission
сохраняет identity с hashes, без снимка карточки. `recovery_source()` требует
точные пути, HEAD и payload fingerprints, а `import_accepted()` затем сравнивает
accepted plan. Поэтому исправление Next вручную не создаёт допустимый переход.
Неудачный resume способен сохранить manifest и recovery_of, но остановиться до
копирования native-plan.json. Такой child нельзя удалить или дополнить планом
задним числом для удобства следующего resume.

Текущий runtime-repair покрывает только ранний stopped original shared-source
run до checkpoint/evidence. Этот change вводит отдельный переход восстановления
плана и не расширяет runtime-repair на поздние стадии.

Локальный потребительский обход подтвердил дополнительный риск: resampling через
`manifest` перезаписывает predecessor manifest. Backup полезен для аудита, но не
удовлетворяет требованию неизменности исходной истории. Последующий handoff
остановился на другой live-board ссылке; новое восстановление не должно обходить
независимые проверки целостности проекта.

## Goals / Non-Goals

**Goals:** точные исходные байты Next; проверенный stopped predecessor со всеми
предками; append-only переход; сохранение завершённых task groups и review usage;
новые proofs перед продвижением; поддержка установленного native predecessor
через явно проверенную смену runtime identity.

**Non-Goals:** новый scope/replan; ручная публикация; восстановление любого текста
карточки; принятие arbitrary patch; изменение профиля/launcher/provider adapters;
отмена операторской остановки; archive/floor/publication reconciliation; изменение
данных или продолжение run конкретного потребителя. Это tooling change, 1С matrix
не применима: native platform и пользовательские инфобазы не затрагиваются.

## Decisions

### 1. Отдельные команды и точная полномочная операция

Предлагаемый CLI: `plan-restore-prepare <run> --reason <text>` и
`plan-restore-apply <run> --proposal <path> --authorize <proposal-sha256>`.
`prepare --dry-run` выводит кандидата и диагностику без записи; обычный prepare
сохраняет proposal и снимки в `.runtime/changerail/plan-restorations/<id>/`.
Команды могут принимать `--accepted-commit` только равный доказанному baseline
run; выбор другого commit не даёт новых полномочий. Apply не запускает модель
или публикацию. После него оператор использует обычный `resume <run>`; receipt
автоматически выбирается только для точно названного predecessor.

Один механизм для одного инварианта. Добавление Next к mutable sections отвергнуто:
это меняло бы ранее принятое решение и смысл старых hashes. Общий replan также
не нужен: Scope/Acceptance и нормализованные artifacts должны остаться прежними.

### 2. Источник байтов и before-state

Prepare под project lock проверяет законченность run, отсутствие writer, точные
HEAD/index/dirty paths, fingerprints последнего manifest и историю recovery_of
без циклов, symlink, пропущенных или чужих владельцев. Переданные run и selected
predecessor фиксируются явно; повторного выбора latest по времени нет.

Accepted-plan origin ищется в ancestry: ближайший подлинный native-plan должен
совпадать с admission receipt и всеми доступными ancestor plans, группами и
change_id. Отсутствие файла у failed child допустимо только при подтверждённом
отказе до import и полном evidence его стадии. Ничего не пишется в child.

Исходную карточку читать из точного Git blob baseline в принятой колонке 2.todo,
проверив единственность карточки/slug и полный accepted card contract. Если blob
не найден или hash не совпал — отказ; произвольный patch не замена источнику.
Для новых admissions сохранить отдельный snapshot accepted card с hash, чтобы
снять зависимость от дальнейшей доступности Git blob. Это не ретроактивное
дополнение старых receipts.

Кандидат заменяет ровно один byte span Next; сохраняются все прочие байты,
включая текущие разрешённые Result/Log, переводы строк и режим файла. Дубликаты
секций, подменённый источник, одновременный drift frozen sections/artifacts,
profile, launcher, adapters или product paths отклоняются до записи. Текущий
payload до восстановления обязан совпадать с последним manifest. После возврата
Next сравнивается вся native identity, не только одно поле hash.

### 3. Неизменяемая транзакция и прерывания

Каталог transition хранит proposal, accepted source reference/blob hash,
before/after card hashes и bytes, точный diff, весь payload inventory, HEAD,
profile/runtime identities, полную history inventory, reason/authority, origin
и predecessor. Ограничения путей/размеров применяются до чтения и записи.

Последовательность: prepared → durable apply-intent → атомарная замена карточки
→ applied receipt с effective manifest → consumption receipt при создании
successor run. Переходы — отдельные файлы с exclusive create и fsync, proposal
не меняется. Под той же project lock apply повторно проверяет все зависимости.

После прерывания разрешено согласовать только записанный intent с одним из
двух точных состояний: before либо after; любое третье состояние блокирует
операцию. Reconcile дописывает недостающую квитанцию, не применяя diff повторно.
Повторный завершённый apply возвращает существующий результат без новой мутации.
Незавершённый intent блокирует обычный run/resume и новый writer до reconcile.
Отдельного автоматического rollback после начала successor нет.

Старые run.json, manifests, native-plan, evidence, phase-events, metrics и
receipts остаются побайтно неизменными, без добавления файлов. Effective manifest
принадлежит transition, содержит before/after fingerprints и ссылку на неизменный
predecessor. Использование существующего `manifest` для пересэмплирования старого
run запрещено. Runtime index может указывать на переход, но не заменяет историю.

### 4. Продолжение, proof freshness и бюджет

Doctor и resume распознают применённый переход, проверяя его owner, whole-history
hashes и effective payload под lock. Новый run имеет recovery_of, указывающий на
последнюю попытку, и restoration reference; accepted plan копируется из
доказанного origin в новый run. Все промежуточные попытки остаются в ancestry.

Завершённые группы сохраняются только при равенстве normalized artifacts,
групп/задач и подтверждённых checkpoint events. Progress checkboxes не являются
самостоятельным доказательством выполнения. Политика нового execution identity
также должна разрешать интерпретацию этих checkpoint без изменения их семантики.

| Сохранённый объект | Действие нового run |
| --- | --- |
| Task semantics и complete events | Наследовать после проверки identity/lineage; не повторять group events. |
| Focused/observed proofs, завязанные на payload | Считать историческими; выполнить нужные проверки заново и получить текущие receipts. |
| Dependency-based reusable proof | Первая версия не переносит автоматически; повторное исполнение по умолчанию. |
| Sync receipt/handoff | Проверить применимость; stale receipt обновить штатной finalize-сессией. Отсутствующий handoff не пропускать. |
| Завершённые review | Сохранить расход; прежний GO не использовать как актуальный GO изменённого payload. |
| Final floor/archive/publication | Не пропускать; незавершённые опасные состояния вне применимости. |

Continuation сначала даёт finalize/repair context с явным списком требуемых
новых evidence, затем обычные review/archive/final/publication gates. При уже
потраченном одном review остаётся один; при двух нет третьего review. В этом
состоянии prepare даёт точную диагностику невозможности дальнейшей доставки
и не предлагает apply как способ получить ещё одну попытку.

### 5. Применимость по стадиям

Допустимы stopped native original и его failed recovery children, завершённые
implementation groups, retained focused evidence, законченные NO-GO review
при оставшемся бюджете. Терминальная причина — drift принятого плана либо
связанная неудачная pre-import recovery попытка; нужен exact manifest.

Исключены: незаконченный writer, явно остановленный оператором run/floor,
незаконченная verification attempt, pending provisional review continuation,
archive intent/archive, начавшиеся final floor или publication. Наличие unrelated
board failure не снимается restoration: следующая штатная проверка обязана его
показать. Post-sync/post-floor repair иных причин — отдельный контракт.

### 6. Установленный predecessor и смена execution identity

Для installed-copy incident новая команда запускается из проверенного нового
runtime с явным `--project`, сначала читая старую установку без её замены.
Prepare с `--runtime-archive <target>` готовит отдельный runtime-transition
proposal; координатор связывает собственную identity и target archive, а не
выдаёт новый процесс за старый frozen code.

Поддержка ограничена проверенными версиями execution-contract/receipt schemas
и точным compatibility descriptor, поставляемым с новым runtime и покрытым
регрессией. Сравнение строк version недостаточно. Descriptor определяет старую
identity shape, допустимые tool file changes и правила наследования checkpoints.
Для incident-class с прежней неполной process_identity пропущенные tool bytes
доказываются полным старым distribution lock/archive, hash которого сохранён
в run. Нельзя достраивать их из текущего непроверенного checkout. Если доказательств
нет, переход отклоняется; profile/launcher/project adapter hashes неизменны.

Под одним project lock apply проверяет обе квитанции и устанавливает только
точный target runtime через distribution transaction, затем применяет Next
restoration. Нужна явная интеграция installer с transition: сейчас он либо
блокирует frozen runs, либо сохраняет их read-only. Не пользоваться
`--retain-history-read-only` для обхода этого ограничения и не удалять старые
записи retained_read_only_runs. Ранее помеченная read-only история никогда не
получает права исполнения. Только проверенная активная lineage допускается
как predecessor нового run; остальные frozen runs блокируют upgrade либо
сохраняются read-only по отдельному существующему разрешению.

Intent учитывает состояния установки (старый/целевой runtime) и карточки
(before/after); прерывание допускает только предусмотренные комбинации и точные
inventory. До полного applied receipt запуск successor невозможен. Исторический
run сохраняет старую identity; отдельная квитанция доказывает разрешённый переход
к полной новой identity. Same-runtime restoration не требует runtime transition.
Shared-source с изменившимся core не включать автоматически в эту совместимость.

## Risks / Trade-offs

- Подмена исходного scope → полный accepted hash, Git blob и exact byte diff.
- Изменение payload между prepare/apply → повторная проверка под одной lock.
- Транзакция из установки и карточки сложнее обычного resume → durable intent,
  тесты прерываний на каждой границе, ограниченный набор состояний.
- Старый runtime не замораживал часть файлов → проверка frozen distribution lock
  и исходного archive; отсутствие доказательства означает отказ.
- Сохранённый checkpoint не гарантирует свежий proof → explicit invalidation
  и текущие receipts перед handoff/review, без копирования старого GO.
- Recovery выбирает child без native-plan → доказанный ancestry origin, без
  записи в child и без потери попытки в review accounting.
- Размер исходной оценки занижен → 6 связанных групп одного change; установка
  и compatibility входят в тот же проверяемый путь, оценки не stop limits.

## Migration Plan

1. Воспроизвести два отказа на текущем source и подготовить installed fixture
   старого schema shape без потребительских файлов.
2. Реализовать prepare/apply/resume transition и negative controls; проверить
   полный synthetic runner path без моделей/сети, с контролируемыми сессиями.
3. Обновить публичный runbook и skill; выпуск нового runtime — отдельное действие.
4. Для реального потребителя сначала подтвердить его актуальное состояние,
   полномочия, доступность before-history и supported compatibility. Локально
   перезаписанный manifest не объявляется прежним сохранённым manifest; такой
   workaround требует отдельного разбора и не принимается автоматически.
5. Перед apply можно отказаться от proposal без изменений payload. После intent
   использовать только reconcile; после successor — штатный status/resume.

## Open Questions

Архитектурных развилок для планирования нет. Точные hashes поддержанного старого
archive и итогового target задаются реализацией/release provenance; матрица
совместимости обязана иметь позитивную synthetic проверку installed incident-class
и отрицательный контроль неизвестной версии до объявления C4 выполненным.
