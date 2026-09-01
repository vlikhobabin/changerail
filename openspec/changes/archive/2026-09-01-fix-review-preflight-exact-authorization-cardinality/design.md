## Context

`scripts/changerail_review_preflight.py` использует `_raw_field`, который
возвращает первое совпадение, и `_reference_matches`, который собирает set
нормализованных references и отвечает только на вопрос о присутствии expected
id. Поэтому второй exact field, duplicate expected edge и дополнительная
dependency authorization source не участвуют в admission decision.

Published contract уже требует two-field successor reference, six-field source
object и reciprocal relations. Новый release-discipline successor дополнительно
зависит от того, что обе dependency edges проверяются fail closed до semantic
review. При этом generic relation parser нельзя делать глобально single-entry:
8 опубликованных authorized successors имеют по 2–4 dependencies, а shared
investigation может блокировать несколько successors. Все 9 опубликованных
authorization sources, напротив, имеют один `## Authorization`, одно field,
один `## Depends On` и одну investigation dependency.

## Goals / Non-Goals

**Goals:**

- сделать bounded-authorization parsing однозначным по field, decoded JSON key
  и relation cardinality;
- сохранить total structured fail-closed result для malformed input;
- не применять card-specific id и не сужать легитимные unrelated board
  relations;
- оставить ceiling, LOC classification, protocol allowance, tracked-HEAD,
  path/id/status, scope и freshness semantics неизменными;
- удержать added production delta не более 150 LOC и проверить boundary через
  production preflight command.

**Non-Goals:**

- менять authorization wire shape или preflight-result schema;
- добавлять authority, provider, credential, execution target, workflow,
  mutation или model-launch surface;
- изменять конкретную authorization-card, successor, release-card, release
  tag, hosted `Release`, assets или `.github/workflows/*`;
- запрещать unrelated dependencies successor или другие targets shared
  investigation;
- реализовывать release successor либо расширять его docs-only authorization
  payload.

## Decisions

### 1. Один bounded JSON field является admission boundary

Parser получает full card text и перечисляет все exact second-level sections и
все field occurrences, а не использует first match. Существующая tolerance к
whitespace, регистру field label и одному полному backtick wrapper сохраняется,
но каждое case-insensitive совпадение учитывается в cardinality, чтобы alternate
casing не обходил duplicate check.

Legacy absence field и ровно одно значение `none` остаются `not-declared`.
Любая non-default successor authorization требует ровно один `## Review` и
ровно одно `Published investigation authorization`. Published source требует
ровно один `## Authorization` и ровно одно `Investigation authorization`.
Duplicate section/field, включая matching плюс unrelated или `none`, дает
structured `invalid`.

Это решение намеренно уточняет более раннюю multi-candidate planning идею:
published authorization card является single-purpose authority source, поэтому
несколько exact source fields больше не селектируются по current target. JSON в
design, prose или другом field/section не является candidate. Такое ужесточение
совместимо со всеми текущими published sources и закрывает ambiguity до
semantic checks.

Alternative: выбирать первый matching object или один объект среди нескольких.
Она отклонена, потому что оставляет неиспользованный exact authorization field в
том же clean authority source и делает его смысл зависимым от target selection.

### 2. JSON декодируется с сохранением top-level pairs

Небольшой общий decoder для двух authorization shapes сохраняет ordered decoded
top-level pairs или эквивалентно обнаруживает duplicate decoded keys до
materialization mapping. Он требует ровно один JSON object и whitespace-only
suffix, отклоняет duplicate keys, затем проверяет exact unique key set и types.

Successor reference имеет только `authorization_card` и `authorization_id` с
non-empty string values. Source object имеет только существующие шесть keys;
четыре identity values являются non-empty strings,
`production_loc_ceiling` — integer-not-boolean `301..500`, а
`allow_new_authority_or_wire_protocol` — boolean. Только после shape/type checks
разрешены path construction, tracked card reads и relation semantics.

Alternative: оставить `json.loads(...)->dict` и сравнивать set keys. Она
отклонена, потому что duplicate decoded key теряется до cardinality check.

### 3. Relation policy различает single-purpose source и shared cards

Generic section enumerator требует ровно один соответствующий `## Depends On`
или `## Blocks`. Reference normalizer сохраняет три допустимые exact формы:
bare id, `<id>.md` и canonical board path. Cardinality считается до set
deduplication, поэтому две эквивалентные формы expected edge являются duplicate.

Для authorization source `## Depends On` является single-purpose relation:
section содержит ровно один non-empty list item, ровно одну нормализуемую card
reference, и она равна authorized investigation. Missing, mismatch, duplicate,
второй item/reference или неоднозначный item invalidates source.

Для successor `## Depends On` и investigation `## Blocks` required expected
edge должен встретиться ровно один раз в единственном section. Другие relations
разрешены: опубликованные successors зависят также от authorization source и
предшественников, а shared investigations блокируют несколько targets.
Duplicate expected aliases invalid; foreign/non-board form не считается
expected, но unrelated relation сама по себе не превращается в authorization.

Alternative: требовать один item во всех трех sections. Она отклонена как
несовместимая с уже опубликованными legitimate workflows.

### 4. Invalid chain сохраняет существующий stop ordering

Любая новая structural/cardinality ошибка возвращает authorization
`status: invalid`. Существующий complexity guard добавляет invalid reason до
fresh-verdict и risk routing, поэтому итог остается exit `1`, outcome
`investigation-required`, `llm_review.required: false` и reason
`complexity guard requires investigation/simplification`. Schema результата не
меняется.

Focused smoke расширяется table-driven mutations одного generic canonical
fixture. Минимальная matrix включает:

- exact positive chain, включая unrelated successor dependency и другой target
  shared investigation;
- duplicate successor published-reference field;
- duplicate source field;
- extra и duplicate decoded JSON key;
- duplicate `## Review`, `## Authorization`, `## Depends On` и `## Blocks`;
- missing, duplicate, mismatched и extra source dependency;
- duplicate expected successor dependency и investigation reference;
- сохранение текущих exact bare/filename/canonical positive forms;
- unchanged ceiling, protocol allowance, tracked/path/id/status и over-ceiling
  negatives.

Каждый negative проверяет exit/outcome/status/detail и отсутствие LLM
eligibility; positive проверяет `valid` и `ready-for-llm-review`.

## Risks / Trade-offs

- [Risk] Ужесточение отклонит unpublished cards с несколькими exact source
  fields, которые прежний first-match parser игнорировал. → Mitigation:
  documented exact-one migration, JSON examples вне exact fields не затронуты,
  а все текущие published patterns заранее проверены как совместимые.
- [Risk] Общая cardinality relation parser может запретить legitimate graph
  edges. → Mitigation: single-entry применяется только к authorization source;
  successor/investigation требуют unique expected edge и сохраняют unrelated
  relations.
- [Risk] Новый helper разрастется в параллельный markdown parser. → Mitigation:
  boundary ограничен exact `##` sections, exact bullet fields и существующими
  backticked reference forms; production budget не более 150 added LOC.
- [Risk] Detail strings сделают smoke brittle. → Mitigation: проверять stable
  class/details только там, где они являются machine oracle; не менять result
  schema.

## Migration Plan

1. Добавить focused RED rows через production preflight command.
2. Реализовать pair-preserving exact-object и section/reference cardinality
   helpers в owning preflight module.
3. Обновить `docs/changerail-contracts.md` и синхронизировать delta
   `changerail-contracts`, явно зафиксировав precedence/compatibility decision.
4. Выполнить focused smoke, compile/lint, strict change/capability/all OpenSpec,
   public scan и whitespace checks; затем sync/archive только в `$changerail-do`.
5. После publish prerequisite заново доставлять исходную authorization-card как
   отдельный unchanged-scope payload.

Rollback удаляет parser tightening, tests и contract wording одним scoped
reviewed change; authorization/release payloads этим change не создаются и не
откатываются.

## Open Questions

- none
