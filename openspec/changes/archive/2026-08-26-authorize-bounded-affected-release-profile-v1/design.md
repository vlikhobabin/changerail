## Context

Published decision `decide-accelerated-release-loop-integration-boundary`
разделяет scheduler execution, affected selection/activation и final
certification. Dormant scheduler v1 уже опубликован; affected profile теперь
должен получить отдельную authorization до создания implementation card.

## Goals / Non-Goals

**Goals:**

- Связать affected profile v1 с published decision, scheduler и future successor.
- Зафиксировать canonical inventory/resolution, bounded Git selector, sole
  scheduler activation и full-only authority.
- Сделать successor absence и zero executable LOC machine-checkable.

**Non-Goals:**

- Не создавать и не реализовывать affected profile v1.
- Не менять runner, CI, receipts, review/publish или scheduler/broker internals.
- Не запускать history, full release baseline, affected execution или live matrix.

## Decisions

### 1. Authorization exact и singular

Эта authorization одна содержит ровно один six-field object:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Future implementation зависит от published decision, scheduler и этой
authorization и использует только:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

Она начинается от authorization-publishing HEAD и добавляет не более 499
production LOC.

### 2. Affected profile владеет selection и sole activation

Future implementation владеет canonical semantic inventory, exact physical
resolution, bounded NUL Git selector и единственным production import/invoke
scheduler v1 из release runner. Она не меняет v5 либо scheduler supervision,
cleanup и result contracts.

Zero args остаются compatibility alias для requested `full-release`, а explicit
`--profile full-release` идентичен. Requested `affected` требует ровно один
`--base`. Selector агрегирует committed, staged, unstaged и untracked paths и
сохраняет old+new operands rename/copy. Любая неопределенность, malformed input,
self-authority change или bounded Git fault выбирает full inventory с
детерминированным fallback reason.

Requested profile навсегда определяет authority: affected всегда
`authoritative:false`, включая успешный full fallback. Только admitted requested
full-release, успешно завершивший exact full inventory, может стать
authoritative. Canonical CI содержит ровно один explicit full runner и не
активирует affected/scheduler/broker/direct semantic commands отдельно.

### 3. Эта delivery docs-only

Successor card и code остаются отсутствующими. Authorization меняет только
card, same-slug artifacts, main spec и archive metadata, с
production/test/runtime LOC 0. History, full baseline, affected или live matrix
не запускаются.

## Risks / Trade-offs

- **Authorization повторяет decision limits** -> exact repetition позволяет
  обнаружить drift до создания successor.
- **Unknown input расширяется до full** -> feedback может быть медленнее, но
  omission невозможен и affected все равно не получает authority.
- **Implementation пока отсутствует** -> это обязательная последовательность;
  successor начинается только от опубликованного authorization HEAD.

## Migration Plan

1. Validate, independently review и publish эту authorization.
2. Только затем создать exact `implement-bounded-affected-release-profile-v1`.

## Open Questions

None. Новые receipts, scheduler/broker изменения, adaptive timing или retry
policy требуют отдельного решения.
