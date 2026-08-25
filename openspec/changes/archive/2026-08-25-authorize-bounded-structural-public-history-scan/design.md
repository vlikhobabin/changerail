## Context

Published decision `8adddfe` завершает investigation
`investigate-structural-public-history-scan-proof` и уже фиксирует exact
ordered lineage. Investigation card находится в `4.done`, blocks как
authorization `authorize-bounded-structural-public-history-scan`, так и
future successor `deliver-structurally-bounded-public-history-scan`, и
`changerail-release-ci` описывает exact six-field authorization object
и exact two-field successor reference.

Generic deterministic preflight принимает только clean tracked
`4.done` source. Поэтому этот change публикует отдельную
authorization card, но не создаёт successor и не изменяет
scanner, tests, release workflow, schemas, helpers, CLI или runtime state.

## Goals / Non-Goals

**Goals:**

- Опубликовать ровно один parser-recognized six-field authorization
  object с exact ids, canonical paths, ceiling `301` и protocol flag
  `false`.
- Сохранить reciprocal investigation/authorization/future-successor
  relations и exact inline source-reference policy.
- Отделить authorization gate ceiling `301` от implementation
  acceptance `<=300` added production LOC against `ccccb625`.
- Подготовить docs-only payload с нулевыми production, test и
  runtime additions.

**Non-Goals:**

- Не создавать future successor card и не реализовывать scanner,
  connected tests, CI checkout или verification helpers.
- Не менять schema/parser, generic authorization semantics, authority,
  wire protocol, credentials или mutation behavior.
- Не запускать history scan, benchmark или full release baseline.
- Не переписывать published decision и не добавлять иные
  successor links.

## Decisions

### 1. Board card остаётся единственным authorization source

Source card содержит одну inline field с exact parser-owned label
`Investigation authorization` и JSON object:

```json
{"investigation_card":"openspec/board/4.done/investigate-structural-public-history-scan-proof.md","investigation_id":"investigate-structural-public-history-scan-proof","successor_card":"openspec/board/3.inprogress/deliver-structurally-bounded-public-history-scan.md","successor_id":"deliver-structurally-bounded-public-history-scan","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

Object содержит только six generic fields. Отдельный JSON/schema
file или новое parser behavior отвергнуты: они создали бы новую
authority/protocol surface вместо публикации уже принятого
generic contract.

### 2. Relation contract связывает три card identities до создания successor

Published investigation `Blocks` authorization и exact future successor.
Authorization `Depends On` investigation и `Blocks` exact future successor.
Future successor, когда отдельный flow создаст его после
publication, `Depends On` investigation и использует в `Published
investigation authorization` только:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}
```

Current investigation card и main release-CI spec уже содержат exact
successor identity. Delivery может только сохранить или восстановить
эту exact relation; создание successor card или любого другого
link не входит в scope.

### 3. Authorization ceiling не повышает implementation budget

`production_loc_ceiling: 301` является минимальным schema-valid
exception ceiling выше generic guard `300`. Normative successor acceptance
отдельно остаётся `<=300` added production LOC от exact baseline
`ccccb62562e1646b595119edd3326763860f14a7`; 301-я production line не
разрешена. Boolean `false` fail-closed запрещает новые authority
и wire protocol.

### 4. Verification остаётся current-file и docs-only

Delivery проверяет strict target/all OpenSpec, JSON/TOML config, current
public-surface scan, source classification, tracked и explicit untracked
whitespace, manifest scope и normalized preflight. History scan, benchmark и
full baseline не запускаются; test files не изменяются. Preflight до
publication может fail-closed на lifecycle gates и не считается
consumption proof future successor.

## Risks / Trade-offs

- **[Risk] Future path drift инвалидирует source.** -> Exact
  `3.inprogress` path является намеренным fail-closed binding; другой
  successor требует нового investigation/authorization flow.
- **[Risk] Ceiling `301` можно ошибочно прочитать как budget.** ->
  Card, spec и design явно сохраняют independent `<=300` acceptance
  against `ccccb625`.
- **[Risk] Authorization нельзя consumировать во время delivery.** ->
  Source становится authoritative только после scoped publication в
  `4.done`; successor до этого не создаётся.

## Migration Plan

1. Delivery сохраняет exact inline source object, синхронизирует
   `changerail-release-ci` delta и архивирует change без code/test/runtime
   additions.
2. Fresh ordinary review проверяет exact object, reciprocal docs и
   zero-LOC scope; publish перемещает source card в `4.done`.
3. Только после remote-reachable publication отдельный flow может
   создать future successor с exact two-field inline reference.

Rollback до publication удаляет только unpublished docs payload. После
publication изменение exact binding требует нового tracked decision,
а не mutation published source.

## Open Questions

Нет. Exact source object, reciprocal relations, inline reference, ceilings и
scope зафиксированы published investigation.
