## Context

Текущий published parser в `scripts/changerail_review_preflight.py` декодирует
authorization source сразу в `dict` и проверяет exact six-field object. Первая
rejected source lineage попыталась сохранить decoded pairs и выбрать current
target до strict validation. Следующая linked-rescue lineage сохранила тот же
подход, но выполняла:

```text
value_id in source_dependencies
```

для каждого decoded `investigation_id` до type validation. Legal JSON pair
`"investigation\u005fid":[]` поэтому передавал unhashable list в set membership,
вызывал `TypeError` и обрывал CLI без structured preflight result. Это один и
тот же defect class в двух последовательных implementation lineages;
same-card rescue budget второй lineage исчерпан `2/2`.

Published investigation
`investigate-phase-routed-resume-integrity-rescue` по-прежнему требует exact
successor `replace-phase-routed-resume-integrity-boundary`, ceiling 500 и
protocol allowance `true`. Однако отклоненные source
`authorize-bounded-phase-routed-resume-integrity-payload` и linked rescue
`rescue-bounded-phase-routed-resume-integrity-authorization` нельзя repair-ить
или публиковать. Нужна новая source identity после отдельного decision-only
investigation.

Граница принадлежит generic review preflight. JSON values недоверенные, JSON
object key после decode всегда строка, но его value может быть любым JSON kind.
Pair order и duplicate decoded keys важны: literal `investigation_id` и
`investigation\u005fid` являются одним decoded key независимо от raw spelling.

## Goals / Non-Goals

**Goals:**

- Определить total/non-throwing algorithm для любого JSON value.
- Никогда не использовать unvalidated identity values в hashing/set membership,
  path construction или semantic relation lookup.
- Сохранить ordered pairs до duplicate, shape и type validation.
- Однозначно упорядочить hint extraction, target selection, duplicate/schema/
  type validation, materialization, semantic checks и review eligibility.
- Зафиксировать полный connected canonical-base matrix и exact structured
  oracle, наблюдающий semantic/model dispatch boundary.
- Назвать одну новую authorization-card, exact six-field object, reciprocal
  relation, implementation ceiling и downstream protocol allowance.
- Исправить circular handoff: review производит `GO`, а publish требует `GO`.

**Non-Goals:**

- Изменять parser, smoke, schemas, CLI, runtime docs или main spec во время FF.
- Repair-ить или публиковать две отклоненные lineage.
- Создавать новую authorization-card или downstream implementation successor.
- Менять six-field authorization wire shape либо phase-routed v1 protocol.
- Ослаблять tracked-HEAD, exact path/id, `Depends On`/`Blocks`, production LOC
  или protocol authorization semantics.
- Добавлять вторую linked rescue, сбрасывать history либо повышать budgets.

## Decisions

### 1. Decode сохраняет pairs и всегда возвращает classified result

Каждое значение exact markdown field `Investigation authorization` извлекается
в document order. JSON из иных sections/inline examples не является candidate.
`JSONDecoder.raw_decode` с `object_pairs_hook` представляет каждый object как
immutable `PairsObject(tuple[(decoded_key, decoded_value), ...])`, включая
nested objects. Parser требует ровно один JSON value и whitespace-only suffix.

Decoder exception не проходит наружу. Boundary возвращает tagged result
`valid | unrelated | invalid` с bounded stable detail. Top-level string,
number, boolean, `null`, array и object без target hints являются unrelated
candidate values; если target candidate в итоге отсутствует, source получает
exact no-current-target invalid result. Это делает функцию total для любого
успешно decoded JSON value. Invalid syntax/trailing value немедленно fail closed
для exact source field.

Rejected: обычный `json.loads` в `dict`, потому что он теряет decoded duplicate
keys и pair order. Rejected: broad regex по JSON prose, потому что semantic
identity принадлежит decoded exact source field, а не raw encoding.

### 2. Hint extraction является linear, typed и non-authoritative

Parser проходит top-level pairs по порядку. Key сравнивается direct equality с
четырьмя trusted literals. Value становится hint только после
`isinstance(value, str) and bool(value)`; остальные types записываются только
как position/type metadata. Никакой raw value не добавляется в `set`/`dict`, не
hash-ится, не передается `Path` и не используется справа от membership.

Trusted target строится только из уже validated current card path/id и source
markdown dependency ids. Для каждого dependency id допустимый investigation
path выводится детерминированно как published board path. Сравнение hints с
trusted strings выполняется nested linear equality, так что даже future custom
JSON containers не могут войти в hash protocol.

Candidate относится к current target, когда содержит:

- хотя бы один exact typed successor hint из `successor_card`/`successor_id`;
- хотя бы один exact typed investigation hint из
  `investigation_card`/`investigation_id`.

Парные hints позволяют single-field type mutation оставаться matching: exact
counterpart выбирает candidate, после чего mutated field получает type detail.
Fully valid distinct target и unrelated object не выбираются. Hint не дает
authority и не заменяет subsequent exact six-field equality.

Rejected: membership decoded `investigation_id` в trusted dependency set до
type check. Rejected: сначала строить mapping/set decoded pairs. Rejected:
выбирать по одному identity field, потому что unrelated examples с похожим id
становятся false-positive target candidates.

### 3. Selection предшествует strict validation, но fail-closed при ambiguity

Parser классифицирует все decoded candidate values и требует ровно один
current-target candidate. Ноль либо больше одного возвращают одинаковый exact
detail `authorization source must contain exactly one matching current target`.
Canonical плюс malformed matching считается ambiguity, а не поводом выбрать
canonical. Canonical плюс unrelated или fully distinct candidate сохраняет
ровно один match и допускает дальнейшую validation.

Malformed matching candidate без второго match выбирается и затем получает
earliest strict detail. Таким образом malformed target невозможно спрятать как
generic no-selection, но unrelated JSON не ломает source selection.

### 4. Strict validation имеет один фиксированный порядок

Для выбранного `PairsObject` выполняется:

1. linear duplicate decoded-key detection над ordered key strings;
2. exact six-key shape validation, включая missing/extra;
3. non-empty string validation для четырех identity values;
4. integer-not-boolean `301..500` validation ceiling;
5. boolean validation protocol allowance;
6. element-wise equality четырех typed identities с current trusted target;
7. materialization unique pairs в mapping;
8. filesystem/path, readable published cards, status, tracked unchanged HEAD и
   reciprocal `Depends On`/`Blocks` semantic relation checks;
9. complexity/protocol authorization и только затем review eligibility.

Duplicate detection может использовать hash только для decoded keys, потому
что JSON grammar гарантирует string keys; предпочтительный implementation —
linear previously-seen comparison, чтобы весь boundary оставался явно
pair-ordered. Identity values не hash-ятся даже после validation: четыре direct
comparisons дешевле и проще аудируются.

Первый failed stage определяет stable detail. Structural/type/selection failures
не вызывают semantic checker. Semantic failures не делают review eligible.
Outer preflight переводит все owned decode/classification/path/I/O errors в
structured invalid state; `TypeError` от input value невозможен по construction.

### 5. Oracle наблюдает owned boundary, а не имитирует model launch

Canonical base — fresh repository с tracked published investigation/source,
exact current successor, 444 production fixture lines, ceiling 500, allowance
true и корректными reciprocal relations. Каждый negative test сначала запускает
этот base через production preflight и доказывает exact valid/ready result,
затем создает независимый fixture с ровно одной mutation.

Structural oracle:

```json
{
  "exit": 1,
  "outcome": "investigation-required",
  "authorization_status": "invalid",
  "authorization_detail": "<exact row detail>",
  "llm_review_required": false,
  "llm_review_reason": "complexity guard requires investigation/simplification",
  "semantic_check_delta": 0,
  "semantic_review_dispatch_delta": 0,
  "model_launch_delta": 0,
  "uncaught_exception": false
}
```

Semantic relation negatives отличаются `semantic_check_delta: 1` и exact
existing relation detail, но сохраняют `semantic_review_dispatch_delta: 0` и
`model_launch_delta: 0`. Smoke запускает production preflight, но не model.
Counter semantic checks является instrumented call count к production relation
stage; semantic-review dispatch наблюдается отдельно и не выводится из
`llm_review.required` либо constant-заглушки. Review eligibility читается из
реального preflight result.

Canonical positive требует exit 0, `ready-for-llm-review`, authorization
`valid`, exact valid detail и `llm_review.required: true`; model counter остается
zero, поскольку orchestration/model launcher вне focused smoke.

### 6. Полная matrix определяется как cross-product

Identity set `K`:

```text
investigation_card, investigation_id, successor_card, successor_id
```

Value set `V`:

```text
exact non-empty string, empty string, distinct non-empty string,
null, true, false, integer 0, float 1.5, array [], object {}
```

Для каждого `K` matrix содержит single replacement каждого `V`. Exact string
проходит; empty/non-string дают exact identity-type detail; distinct string
дает exact identity-target-mismatch detail. Equivalent legal escapes одного
key и его exact value отдельно являются positives.

Duplicate matrix — полный `K × V × O`, где `O` содержит оба order:

```text
literal key/value first, alternate-escaped decoded-equal key/V second
alternate-escaped decoded-equal key/V first, literal key/value second
```

Literal occurrence использует canonical exact value; когда `V` тоже exact,
получается same-value duplicate. Все rows обязаны дать exact duplicate detail
до type/schema/semantic dispatch. Это явно включает array/object-first cases,
которые отсутствовали в rejected matrix.

Дополнительные connected groups:

- top-level JSON kinds и invalid/trailing JSON;
- missing каждого из шести fields и один extra field;
- ceiling boundary/type и allowance type independently;
- canonical/unrelated/distinct/malformed combinations: zero, one и multiple
  matching candidates;
- current source/successor/investigation path/id/status/tracked and reciprocal
  relation mutations.

Для canonical + unrelated и canonical + valid distinct exact match один и
проходит. Unrelated/distinct-only дает zero-match. Два canonical или canonical
плюс malformed matching дают ambiguity. Malformed matching alone доходит до
earliest strict validation detail. JSON outside exact field не извлекается.

Rejected: sampling только `successor_id` или только string duplicates.
Rejected: одна shared mutable fixture без отдельного canonical-base pass.
Rejected: утверждать model-launch absence через constant либо через сам
`llm_review.required`.

### 7. Выбрана одна новая authorization identity

Следующий work item:

- id: `authorize-type-safe-phase-routed-resume-integrity-payload`;
- initial path:
  `openspec/board/2.todo/authorize-type-safe-phase-routed-resume-integrity-payload.md`;
- published path:
  `openspec/board/4.done/authorize-type-safe-phase-routed-resume-integrity-payload.md`.

Relations:

- authorization `Depends On`
  `investigate-type-safe-decoded-target-classification-boundary`;
- authorization `Blocks` `replace-phase-routed-resume-integrity-boundary`;
- investigation reciprocally `Blocks` authorization и successor;
- successor later references only the new published source.

Authorization implementation ограничивается
`scripts/changerail_review_preflight.py`, connected
`scripts/smoke-review-preflight.py`, its card/change/spec artifacts и имеет
ordinary hard ceiling 300 added production LOC. Это не bounded exception для
самого parser fix.

Published source содержит ровно один six-field object:

```json
{"investigation_card":"openspec/board/4.done/investigate-type-safe-decoded-target-classification-boundary.md","investigation_id":"investigate-type-safe-decoded-target-classification-boundary","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Successor reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-type-safe-phase-routed-resume-integrity-payload.md","authorization_id":"authorize-type-safe-phase-routed-resume-integrity-payload"}
```

Ceiling 500 относится к atomic downstream phase-routed successor и сохраняет
12-line headroom над measured 488-line candidate; `501+` останавливает его для
новой split investigation. Protocol allowance `true` сохраняется, потому что
phase-routed v1 writer/validator authority еще не опубликована. Parser-fix item
не меняет wire schema и сам остается в ordinary 300-line boundary.

Rejected source/rescue ids не переиспользуются: их payloads остаются
forensic-only и никогда не получают repair/publish. Новая identity исключает
неоднозначность published tracked-HEAD source lineage.

### 8. Review получает GO, publish потребляет GO

После implementation, verification, spec sync и archive новый authorization
item остается `3.inprogress` и передается `$changerail-review ...` без GO как
precondition. Fresh independent review создает `GO` или `NO-GO`. Только fresh
`GO` разрешает `$changerail-pub ...` и deterministic finalization в `4.done`.
Implementation successor нельзя создавать до публикации current investigation
и new authorization source.

## Risks / Trade-offs

- [Risk] Linear pair/candidate comparison добавляет code paths. → Mitigation:
  четыре identity keys и шесть total fields дают bounded input; totality и
  auditability важнее микрооптимизации.
- [Risk] Canonical плюс malformed matching классифицируется как ambiguity, а не
  сообщает inner type. → Mitigation: exact one-target invariant fail closed;
  standalone malformed rows сохраняют точный inner detail.
- [Risk] Fully distinct candidates игнорируются рядом с one exact candidate. →
  Mitigation: authority связывается только exact current target; separate
  zero/multiple controls доказывают отсутствие fail-open для current target.
- [Risk] Exact detail strings могут стать brittle. → Mitigation: они являются
  machine oracle этой security boundary и изменяются только вместе со spec.
- [Risk] Ceiling 500 downstream остается узким. → Mitigation: он уже выбран
  published phase-routed investigation; parser fix delivered отдельно в
  <=300 LOC и не расходует downstream measured delta.

## Migration Plan

1. Deliver этот decision-only change, синхронизировать ровно один
   `changerail-contracts` requirement, получить fresh independent review и
   publish. Runtime migration отсутствует.
2. После publish создать только
   `authorize-type-safe-phase-routed-resume-integrity-payload` с declared
   relation/object. Не копировать rejected source/rescue cards или archives.
3. Реализовать total parser и full connected matrix в <=300 production LOC,
   выполнить review для получения GO и только после GO publish/finalize source.
4. Лишь после published source создать
   `replace-phase-routed-resume-integrity-boundary` с exact two-field reference,
   critical review, production ceiling 500 и protocol allowance true.
5. Не продолжать pilot wave до публикации successor.

Rollback current investigation документационный. Поздний parser rollback
должен одновременно удалить новую source authority; downstream successor не
может ссылаться на absent/stale source.

## Open Questions

- none
