## Context

Published rescue decision `e51dbae` завершает
`rescue-tiered-release-authority-two-stage-boundary` и фиксирует отдельные A1
passive admission/registry и A2 terminal authority lineages. Неопубликованный
broad Scope A payload не прошёл pre-capture audit и остаётся forensic-only.

Generic deterministic preflight принимает investigation-required exception
только из clean tracked `4.done` authorization source. Поэтому этот change
публикует отдельную authorization card для будущего A1, но не создаёт
implementation successor, не активирует A1 и не изменяет executable surfaces.

## Goals / Non-Goals

**Goals:**

- Опубликовать ровно один parser-recognized six-field authorization object с
  exact rescue/future-A1 identities, ceiling `500` и protocol flag `false`.
- Сохранить reciprocal rescue/authorization/future-successor relations и exact
  two-field inline source reference для будущего A1.
- Ограничить future A1 passive ownership и доказуемую structural dormancy.
- Сделать focused/static/offline/current checks единственным допустимым
  deterministic publication proof этой authorization и будущего A1.
- Подготовить docs-only payload с нулевыми production, test и runtime
  additions.

**Non-Goals:**

- Не создавать карточку или код `implement-passive-release-admission-registry`.
- Не реализовывать, копировать или ремонтировать forensic broad Scope A.
- Не активировать A1 из baseline, CI, manifest/review/pub preflight, receipt
  schemas или production entrypoints.
- Не создавать A2 authority, receipt, wire protocol, credentials, mutation или
  live-access behavior.
- Не запускать history scan, full release baseline или terminal capture.

## Decisions

### 1. Board card является единственным authorization source

Source card содержит одну inline field с exact parser-owned label
`Investigation authorization` и JSON object:

```json
{"investigation_card":"openspec/board/4.done/rescue-tiered-release-authority-two-stage-boundary.md","investigation_id":"rescue-tiered-release-authority-two-stage-boundary","successor_card":"openspec/board/3.inprogress/implement-passive-release-admission-registry.md","successor_id":"implement-passive-release-admission-registry","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":false}
```

Object содержит только six generic fields. Отдельный schema, parser или
authority surface не создаются: они нарушили бы protocol `false` и вышли бы за
рамки уже опубликованного rescue.

### 2. Reciprocal lineage связывает future A1 без его создания

Published rescue blocks authorization и exact future A1. Authorization
depends on rescue и blocks exact future A1. Когда отдельный flow после
remote-reachable publication создаст successor, тот depends on rescue и
содержит в `Published investigation authorization` только:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-passive-release-admission-registry.md","authorization_id":"authorize-bounded-passive-release-admission-registry"}
```

На FF/DO/review/pub authorization-карточки future successor должен оставаться
отсутствующим. Его раннее создание делает lineage fail-closed.

### 3. Ceiling связывается с будущим published authorization HEAD

`production_loc_ceiling:500` допускает bounded exception, но normative A1
acceptance остаётся `<=499` added production LOC. Comparison base не является
decision commit или текущий FF HEAD: будущая implementation обязана сравнивать
с exact remote-reachable HEAD, который опубликует эту authorization card.
Boolean `false` запрещает A1 получать новую authority или wire protocol.

### 4. A1 ownership остаётся passive и закрытым

Future A1 может владеть только literal 35-record semantic registry, canonical
digest, owners/direct commands/sequential groups, injected total bounded
offline admission, effective-PATH Python, parsed distribution pins и Ruff
origin, offline OpenSpec admission, bounded Git A/M/D/R/C/untracked selector,
closed path map, parsed Python-AST ownership oracle и connected fault cases.
Missing, duplicate, unknown, malformed, ambiguous, over-limit или unavailable
input fail closed до запуска admitted semantic command.

До публикации exact A2 ни один authoritative surface не может import, invoke
или activate A1. После неё только exact published
`implement-terminal-release-authority-activation` может это делать; любая
другая wiring path является ownership violation.

### 5. Authorization и dormant A1 используют только релевантный proof

Детерминированный gate этой docs-only authorization ограничен strict OpenSpec,
exact-object/lineage/absence/ownership assertions, JSON/TOML parsing,
current-only public scan, source classification, whitespace и scoped
preflight. Future A1 дополнительно доказывает real offline admission,
focused/static/current behavior и connected faults.

History scan, full baseline, authority receipt и terminal capture не наблюдают
dormant A1 и поэтому MUST NOT выполняться, требоваться или приниматься как
publication evidence. Они также не могут стать reusable pass для A2.

## Risks / Trade-offs

- **[Risk] Future successor path drift.** -> Exact ids и canonical paths
  fail-closed; другой successor требует новой authorization lineage.
- **[Risk] Ceiling ошибочно прочитают как разрешение 500 production lines.** ->
  Implementation ограничена `<=499` относительно exact published
  authorization HEAD.
- **[Risk] Отсутствие full baseline скроет integration defect.** -> Integration
  намеренно отсутствует и доказывается negative-wiring oracle; A2 отдельно
  владеет единственной activation и terminal capture.
- **[Risk] Dormant library получит authority через documentation drift.** ->
  Protocol `false`, closed ownership и запрет receipt/entrypoint wiring делают
  drift deterministic failure.

## Migration Plan

1. DO синхронизирует exact release-CI delta и архивирует sole docs-only change
   без создания future A1.
2. Fresh independent review проверяет exact object, reciprocal lineage,
   ownership/dormancy, successor absence и focused/current-only gate.
3. Publish перемещает authorization source в `4.done`; его exact
   remote-reachable HEAD становится comparison base future A1.
4. Только после publication отдельный flow создаёт future A1 с exact two-field
   reference.

Rollback до publication удаляет только unpublished docs payload. После
publication exact binding меняется новой tracked decision/authorization, а не
mutation опубликованного source.

## Open Questions

Нет. Exact source, ownership, dormancy, proof boundary и publication order
зафиксированы published rescue.
