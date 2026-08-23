# Исследовать type-safe классификацию decoded authorization target

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Fresh independent review cycle 3 карточки
  `rescue-bounded-phase-routed-resume-integrity-authorization` завершился
  `NO-GO`: same-card rescue budget исчерпан `2/2`.
- Reviewed payload fingerprint:
  `sha256:055a2c39a2429cda1b6503082b03ca168cec2768f26f4d491cf76a1e0e60bd9f`.

## Summary
Опубликовать decision-only investigation для total и type-safe классификации
декодированных authorization target fields до любой semantic membership,
hashing или relation проверки. Исследование должно выбрать точный алгоритм,
полную connected regression matrix и следующий policy-compliant replacement
authorization path после исчерпания source и linked-rescue payloads.

Отклоненные payloads являются только forensic input: эта карточка не делает им
еще один repair, не публикует их и не создает implementation successor.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Карточка decision-only: production code, schemas, tests, CLI и runtime behavior
не изменяются.

## Depends On
- none

## Blocks
- Создание и delivery replacement authorization work item
  `authorize-type-safe-phase-routed-resume-integrity-payload`.
- Любое дальнейшее исправление или публикацию authorization lineage для
  `replace-phase-routed-resume-integrity-boundary`.
- Создание и delivery implementation successor
  `replace-phase-routed-resume-integrity-boundary`.
- Продолжение pilot wave phase-routed batch runner.

## Decision Questions
- Как pair-preserving parser должен total/non-throwing классифицировать JSON
  objects, если identity fields содержат string, array, object, null, boolean
  или number, включая duplicate decoded keys в обоих порядках.
- В каком порядке должны выполняться target hint extraction, duplicate/schema/
  type validation, exact target selection и semantic relation checks, чтобы
  недоверенное значение никогда не использовалось как hash/set member до
  проверки типа.
- Как отличать malformed matching candidate от unrelated JSON и distinct valid
  target без fail-open и без Python exception.
- Какая connected canonical-base matrix обязана доказывать structured
  fail-closed result, exact reason и отсутствие semantic/model dispatch для
  каждого identity field и JSON type/order.
- Какой exact replacement authorization card, successor relation, bounded
  production LOC ceiling и protocol allowance допустимы после исчерпания двух
  последовательных implementation lineages одного defect class.

## Selected Decisions

### Total pair-preserving classification

1. Parser извлекает все значения только exact markdown field
   `Investigation authorization` в document order. JSON вне этого field не
   является authorization candidate. Каждое field value декодируется ровно как
   один JSON value через `JSONDecoder.raw_decode` с `object_pairs_hook`, который
   сохраняет каждый object как immutable ordered pairs; trailing non-whitespace
   и decode failure дают structured invalid result.
2. До любого `dict`, `set`, hashing, path construction или relation lookup
   выполняется linear hint extraction. Для decoded object parser проходит пары
   по порядку и сравнивает key только с четырьмя trusted literal names:
   `investigation_card`, `investigation_id`, `successor_card`, `successor_id`.
   Hint существует только если value уже проверен как non-empty `str`; array,
   object, `null`, boolean и number не сравниваются через membership и не
   становятся hash keys/set members.
3. Current-target candidate обязан иметь хотя бы один exact typed successor
   hint (`successor_card` или `successor_id`) и хотя бы один exact typed
   investigation hint (`investigation_card` или `investigation_id`), выведенный
   из trusted current card и source `Depends On`. Сравнение выполняется
   element-by-element, без set membership над decoded values. Unrelated object
   без такой пары hints и fully valid distinct target не выбираются.
4. Ровно один current-target candidate выбирается до strict validation. Ноль
   дает `authorization source must contain exactly one matching current target`;
   два и более, включая canonical плюс malformed matching candidate, дают тот
   же fail-closed detail. Невыбранные unrelated/distinct candidates не
   запускают semantic checks.
5. Для выбранного candidate validation идет строго в таком порядке: duplicate
   decoded keys по сохраненным pairs; exact six-key shape без missing/extra;
   non-empty string type для четырех identity fields; integer-not-boolean range
   `301..500` для `production_loc_ceiling`; boolean type для
   `allow_new_authority_or_wire_protocol`; exact typed target equality. Только
   после этого pairs материализуются в mapping и начинаются filesystem,
   tracked-HEAD, `Depends On`/`Blocks` и остальные semantic relation checks.
6. Classification boundary total/non-throwing для любого JSON value: ожидаемые
   decode, type, range, duplicate, selection, path и relation failures
   преобразуются в один structured invalid state. Ни один input-dependent
   Python exception не выходит в CLI, а raw decoded identity value никогда не
   участвует в hashing или set membership даже после неудачной проверки.

### Exact structured oracle и dispatch boundary

- Passing canonical base возвращает exit `0`, `outcome:
  ready-for-llm-review`, authorization `status: valid`, detail `published
  authorization source binds the exact successor` и `llm_review.required:
  true`. Focused smoke не запускает model, поэтому `model_launch_delta: 0`.
- Каждый classification/schema/type negative возвращает exit `1`, `outcome:
  investigation-required`, authorization `status: invalid`, exact row detail,
  `llm_review.required: false`, reason `complexity guard requires
  investigation/simplification`, `semantic_check_delta: 0`,
  `semantic_review_dispatch_delta: 0`, `model_launch_delta: 0` и
  `uncaught_exception: false`.
- Exact details: invalid/trailing JSON — `authorization JSON must contain
  exactly one value`; zero/multiple match — `authorization source must contain
  exactly one matching current target`; duplicate — `authorization source
  contains duplicate decoded key: <key>`; shape — `authorization source must
  contain exactly the required fields`; identity type — `authorization source
  identity field <key> must be a non-empty string`; typed mismatch —
  `authorization source identity field <key> does not match the current
  target`; ceiling and allowance retain exact existing range/type details.
- Semantic checks receive only one validated typed mapping. Их negative rows
  используют существующие exact path/id/tracked/relation details, имеют
  `semantic_check_delta: 1`, но сохраняют
  `semantic_review_dispatch_delta: 0`, `llm_review.required: false` и
  `model_launch_delta: 0`. Semantic-review/model dispatch до успешного
  завершения всех semantic checks запрещен.

### Connected canonical-base matrix

Каждая строка ниже создается из собственного fresh fixture. Сначала неизмененный
canonical six-field source с ceiling `500`, allowance `true` и корректными
relations проходит тот же production preflight; затем применяется ровно одна
mutation, и harness записывает `base_status`, mutation id, exit, outcome,
authorization status/detail, `llm_review`, semantic/model counters и отсутствие
exception.

| Matrix | Полный набор строк | Exact outcome |
| --- | --- | --- |
| Identity type/value | Для каждого из четырех identity keys отдельная replacement mutation на exact string, empty string, distinct string, `null`, `true`, `false`, integer `0`, float `1.5`, array `[]`, object `{}` | Exact string — canonical pass; empty и все non-string — `<key> must be a non-empty string`; distinct string — `<key> does not match the current target`; negative dispatch counters as above |
| Alternate escaped single key/value | Для каждого identity key literal spelling заменяется эквивалентным `\u`-escaped decoded key; path/id value отдельно получает equivalent legal JSON escaping | Canonical pass; pair order и decoded value сохраняются |
| Alternate-escaped duplicate cross-product | Для каждого identity key и каждого value из exact string, empty string, distinct string, `null`, `true`, `false`, `0`, `1.5`, `[]`, `{}` добавляется decoded-equal `\u`-escaped duplicate: сначала literal/потом escaped и сначала escaped/потом literal | Всегда exact duplicate detail для этого key до type/schema/semantic dispatch; это включает array-first и object-first orders |
| Shape | По одной mutation удаляет каждый из шести required fields; отдельная mutation добавляет `extra`; top-level принимает каждый JSON kind: object, string, array, `null`, boolean, integer и float | Matching missing/extra — exact required-fields detail; non-object/no-hint — exact one-current-target detail; без exception/dispatch |
| Ceiling/allowance | Ceiling `301`, `499`, `500`; затем `300`, `501`, `true`, `false`, `null`, string, float, array, object. Allowance `true`, `false`; затем `null`, number, string, array, object | In-range integer-not-boolean и both booleans structurally pass; invalid rows получают exact existing range/type detail before semantics |
| Candidate selection | Canonical alone; canonical + unrelated exact-field object; canonical + valid distinct target; unrelated alone; one distinct alone; two distinct; two canonical; canonical + malformed matching; malformed matching alone; unrelated JSON outside exact field; no exact field | Ровно один matching canonical проходит; zero/multiple matching получает exact one-current-target detail; malformed selected candidate получает его earliest duplicate/shape/type detail; outside-field JSON ignored |
| Semantic relations | От canonical base отдельно меняются source/card path/id, published status/tracked state, successor equality, investigation `Depends On`, investigation `Blocks`, source `Depends On` | Exact existing semantic detail, `semantic_check_delta: 1`, `semantic_review_dispatch_delta: 0`, no model dispatch |

Matrix является cross-product, а не sampling: четыре identity keys проходят все
single-value rows и все duplicate value/order rows. Fake objects могут считать
semantic/model calls, но production `_published_investigation_authorization`
остается единственной admission boundary.

### Единственный следующий authorization work item

- Следующий и единственный допустимый item:
  `authorize-type-safe-phase-routed-resume-integrity-payload`; initial path
  `openspec/board/2.todo/authorize-type-safe-phase-routed-resume-integrity-payload.md`;
  published source path
  `openspec/board/4.done/authorize-type-safe-phase-routed-resume-integrity-payload.md`.
- Он `Depends On`
  `investigate-type-safe-decoded-target-classification-boundary` и `Blocks`
  `replace-phase-routed-resume-integrity-boundary`; current investigation
  reciprocally blocks both. Его implementation ограничен parser и connected
  smoke, не меняет schemas/runner/CLI/runtime docs и имеет ordinary hard ceiling
  `300` added production LOC.
- Published source содержит ровно один object:
  `{"investigation_card":"openspec/board/4.done/investigate-type-safe-decoded-target-classification-boundary.md","investigation_id":"investigate-type-safe-decoded-target-classification-boundary","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
- Будущий successor ссылается ровно на
  `{"authorization_card":"openspec/board/4.done/authorize-type-safe-phase-routed-resume-integrity-payload.md","authorization_id":"authorize-type-safe-phase-routed-resume-integrity-payload"}`.
  Ceiling `500` и protocol allowance `true` сохраняют опубликованное atomic
  phase-routed решение; `501+` требует новой investigation/split authorization.
- Отклоненные
  `authorize-bounded-phase-routed-resume-integrity-payload` и
  `rescue-bounded-phase-routed-resume-integrity-authorization` остаются
  forensic-only. Они не repair-ятся, не публикуются и не являются source для
  нового item. Эта карточка не создает ни новый authorization item, ни
  implementation successor.

### Non-circular handoff

- После implementation/verification authorization item передается напрямую в
  `$changerail-review` для получения fresh independent `GO`.
- `GO` не является prerequisite review; он требуется только перед
  `$changerail-pub` и deterministic finalization. До публикации investigation
  и нового authorization source implementation successor не создается.

## Acceptance
- Выбран deterministic двухфазный или эквивалентный алгоритм, который является
  total для любого JSON value и не hash-ит непроверенные identity values.
- Для `investigation_card`, `investigation_id`, `successor_card` и
  `successor_id` определена матрица всех JSON scalar/container types,
  alternate-escaped duplicate keys в обоих порядках, missing/extra fields,
  unrelated JSON, distinct targets и multi-candidate input.
- Каждый negative probe начинается с passing canonical base, изолирует одну
  mutation и проверяет structured outcome/status/detail, review/dispatch
  eligibility и отсутствие uncaught exception.
- Назван один policy-compliant следующий work item и exact authorization
  contract либо явно доказана необходимость дополнительного split; rejected
  payloads не получают repair и не публикуются.
- Investigation остается planning-only, проходит fresh independent review и
  публикуется до создания любого replacement authorization или implementation
  successor.
- Review handoff описан без circular prerequisite: review получает fresh `GO`,
  а `GO` требуется только для publish/finalization.

## Non-Goals
- Исправлять `scripts/changerail_review_preflight.py` или smoke tests в этой
  карточке.
- Делать второй linked rescue поверх исчерпанного rescue payload.
- Публиковать `authorize-bounded-phase-routed-resume-integrity-payload` или
  `rescue-bounded-phase-routed-resume-integrity-authorization`.
- Создавать `replace-phase-routed-resume-integrity-boundary` до опубликованной
  authorization lineage.
- Сбрасывать review history или увеличивать rescue budget.

## Change Set
- `decide-type-safe-decoded-target-classification-boundary`

## Verify
- Planning gate:
  `bin/openspec validate decide-type-safe-decoded-target-classification-boundary --strict`.
- Final planning floor: `bin/openspec validate --all --strict`,
  `git diff --check` и explicit whitespace scan всех untracked files.

## Archive
- `openspec/changes/archive/2026-08-23-decide-type-safe-decoded-target-classification-boundary/`

## Related
- `openspec/board/4.done/investigate-phase-routed-resume-integrity-rescue.md`
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `openspec/changes/archive/2026-08-23-decide-type-safe-decoded-target-classification-boundary/`

## Result
Decision-only investigation selected, verified, synced as one
`changerail-contracts` requirement and archived. Production/runtime surface,
authorization card and implementation successor не создавались.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change Plan Notes
Ровно один decision-only OpenSpec change может синхронизировать один normative
decision requirement в `changerail-contracts` только во время apply. Fast
forward не меняет main spec, production/runtime surface и не материализует
successors.

## Change 1: `decide-type-safe-decoded-target-classification-boundary`

### Why
Один defect class повторился в source authorization и следующей linked-rescue
lineage: decoded identity value использовалось в set membership до проверки
типа и разрушило structured fail-closed boundary.

### Goal
Опубликовать total type-safe classification decision, исчерпывающую connected
matrix и единственный новый authorization path без runtime implementation.

### Scope
- Зафиксировать ordered pair-preserving algorithm и exact structured oracle.
- Зафиксировать полную identity/type/duplicate-order/candidate/relation matrix.
- Назвать один новый authorization item, reciprocal relations, exact source
  object, ceiling и protocol allowance.
- Не изменять production code, schemas, tests, CLI, runtime docs/behavior и не
  создавать authorization/successor cards.

### Acceptance
- Все card-level acceptance criteria представлены normative delta scenarios и
  ordered delivery tasks.
- Change остается apply-ready decision-only единицей с fresh review handoff без
  circular `GO` prerequisite.

### Depends On
- none

### Related
- `openspec/changes/decide-type-safe-decoded-target-classification-boundary/`

## Log
- 2026-08-23T13:56:31Z создана после fresh cycle-3 `NO-GO`: array-valued first
  occurrence alternate-escaped `investigation_id` вызвал uncaught `TypeError`
  до structured fail-closed output; linked-rescue budget исчерпан `2/2`.
- 2026-08-23T14:11:15Z `$changerail-ff` выбрал total pair-preserving algorithm,
  exact fail-closed oracle, full connected matrix и единственный новый
  authorization item; создан один apply-ready decision change без production,
  successor, review или publish действий.
- 2026-08-23T14:22:51Z `$changerail-do` синхронизировал ровно один requirement,
  архивировал decision change и передал карточку в independent review; fresh
  review производит `GO` или `NO-GO`, а `GO` нужен только для publish.
- 2026-08-23T14:24:32Z preflight отделил historic repeated defect от текущего
  decision-only payload: риск metadata уточнены до `Repeated defect class: no`;
  это investigation/simplification, а не повторная implementation lineage.
- 2026-08-23T15:03:05Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
