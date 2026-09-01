## Context

Published investigation
`openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md`
является normative decision source для exact successor
`enable-post-commit-release-resume-entry`. Оно измерило predecessor baseline
`299` production-counted LOC, выбрало successor forecast `359..399`, planned
increment не больше `100` строк и потребовало отдельную authorization-card с
hard ceiling `400` и protocol allowance `false`.

Authorization должна быть опубликована до добавления two-field reference в
successor. Поэтому отсутствие exact live successor path или reciprocal
successor edge на стадии этой card не исправляется здесь: canonical preflight
обязан fail closed, пока отдельная последующая сессия не обновит exact
successor после publication authorization source.

## Goals / Non-Goals

**Goals:**

- создать один clean tracked docs/OpenSpec authorization source;
- сохранить exact six-field key set, типы, identities, paths и значения из
  published investigation;
- нормативно связать authorization и successor с тем же exact investigation;
- задать deterministic fail-closed consumption для любой неполной или
  mismatched chain;
- сохранить planned successor budget и hard ceiling как разные ограничения.

**Non-Goals:**

- изменять, перемещать или реализовывать successor card в этой delivery;
- добавлять successor authorization reference до публикации source;
- менять production/runtime/test code, preflight implementation или fixtures;
- создавать schema, provider, credential, workflow, execution target, wire
  protocol или mutation authority;
- изменять release-card, создавать tag, GitHub Release, assets или выполнять
  любую release mutation.

## Decisions

### 1. Board card является единственным authorization source

Authorization-card содержит ровно одну строку `Investigation authorization`
с одним JSON object. Object имеет только шесть schema-defined полей; exact
values перечислены в delta spec и совпадают с published investigation.
Proposal/design/spec не становятся дополнительными waiver sources: они
описывают contract, а canonical preflight потребляет только clean tracked
published card в `4.done`.

Rejected: inline waiver в successor или копия JSON в release-card. Такие
источники нельзя независимо опубликовать и связать с exact investigation.

### 2. Planned budget не повышается до schema ceiling

Measured baseline остаётся `299`, investigated exact successor forecast —
`359..399`, planned increment — максимум `100` counted строк. Значение `400`
остаётся machine-readable hard ceiling authorization contract, а не новым
плановым target и не разрешением расширить investigated surface. Measurement
`401+` всегда останавливает semantic review для split/new investigation.

Rejected: использовать net LOC, менять source classification или удалять
regression coverage ради count. Эти действия изменили бы normative decision,
которую authorization-card не вправе расширять.

### 3. Dependency chain завершается только после publication

Эта authorization-card объявляет `Depends On` exact published investigation.
После её review/publish отдельная successor session должна обеспечить exact
`3.inprogress` identity/path, добавить тот же investigation id в successor
`Depends On` и exact two-field reference на published authorization source.
Canonical deterministic preflight принимает chain только при совпадении всех
трёх tracked cards и fail closed до semantic review при missing, unpublished,
duplicated, extra или mismatched field, id, path, edge или reference.

Rejected: менять successor сейчас. Reference на ещё не опубликованную card не
является действующей authorization и нарушает заданный publication order.

### 4. Apply scope ограничен OpenSpec lifecycle

Delivery синхронизирует один ADDED requirement в существующую capability
`changerail-release-discipline`, архивирует change и обновляет metadata этой
card. Existing canonical preflight уже владеет generic parsing и reciprocal
relation behavior; authorization change не добавляет production или test
implementation. Existing deterministic smoke может использоваться как
регрессионная проверка без изменения fixtures.

Rejected: включить successor runtime/test work или release mutation в один
payload. Это разрушило бы независимость authorization source и смешало бы
решение с его потребителем.

## Risks / Trade-offs

- **[Risk] JSON prose drift создаст похожий, но иной waiver.** → Хранить
  machine-readable object ровно один раз на card; delta spec перечисляет exact
  key set, types и values, а delivery сверяет semantic equality.
- **[Risk] Отсутствующий successor примут за готовую positive chain.** → До
  отдельного post-publication successor update expected result остаётся
  fail-closed; эта card не подделывает reciprocal edge.
- **[Risk] Ceiling `400` примут за planned increment `101`.** → Card/spec/design
  отдельно сохраняют planned `<=100` и forecast `359..399`; hard ceiling не
  расширяет implementation boundary.
- **[Risk] Release-critical docs source воспримут как release authority.** →
  Protocol allowance остаётся `false`, scope исключает release objects и
  mutation, а card получает отдельный critical review/publish.

## Migration Plan

1. Через `$changerail-do` доставить только card/OpenSpec payload,
   синхронизировать один delta requirement и архивировать change.
2. Получить independent review и publish authorization-card в exact `4.done`
   path без release mutation.
3. В отдельной сессии после publication обновить exact successor: сохранить
   investigation dependency и добавить exact two-field authorization
   reference.
4. Перед successor semantic review выполнить canonical deterministic preflight
   exact chain и cumulative LOC measurement; при `401+` остановиться для split
   или нового investigation.

До publication rollback удаляет только непубликованный docs/OpenSpec payload
обычным reviewed flow. После publication отмена authorization требует новой
tracked card; release objects эта change не создаёт и не удаляет.

## Open Questions

- none
