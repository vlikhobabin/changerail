# Авторизовать bounded affected release profile v1

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 06

## Source
- Published integration decision
  `decide-accelerated-release-loop-integration-boundary`, commit
  `0de81cf7e578335c728466b81c1c60b6d447dab7`.
- Published dormant scheduler implementation
  `implement-bounded-release-semantic-scheduler-v1`, commit
  `1414fd744eab565258d590a18fe687e39461b9af`.

## Summary
Опубликовать ровно одну docs-only authorization для affected release profile
v1 после опубликованного scheduler v1, не создавая successor, не активируя
runner/CI и не запуская release evidence.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `implement-bounded-affected-release-profile-v1`

## Authorization
- Investigation authorization:
  `{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Карточка содержит ровно один ordered six-field object, равный published
  decision, зависит от decision и published scheduler и блокирует только exact
  affected-profile implementation.
- Future implementation зависит от всех published predecessors и использует
  только `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}`.
- Implementation начинается от будущего authorization-publishing HEAD,
  добавляет не более `499` production LOC, импортирует published scheduler v1
  ровно в release runner и не переопределяет broker/scheduler internals.
- Она владеет canonical semantic inventory, exact physical resolution и
  bounded NUL selector для committed, staged, unstaged и untracked Git state с
  old+new operands для rename/copy.
- Невалидный/non-ancestor base, framing/status/path/bound/Git fault, unknown,
  ambiguous или authority-self change детерминированно выбирает full inventory
  и bounded fallback reason без release authority.
- Zero args и explicit `--profile full-release` идентичны; affected требует
  ровно один `--base` и всегда `authoritative:false`, включая full fallback.
- Canonical CI сохраняет ровно один active explicit full-release runner;
  review, publish, receipt и certification не принимают affected output как
  full-release evidence.
- Successor card/code отсутствуют; authorization меняет только docs/OpenSpec,
  добавляет production/test/runtime LOC `0` и не запускает history/full/live.

## Change Set
- `authorize-bounded-affected-release-profile-v1`

## Verify
- GREEN: FF strict target/all OpenSpec, exact object/reference/decision equality,
  published decision+scheduler reachability, sole-block and successor-absence.
- GREEN: DO synchronized capability/all strict OpenSpec, exact archive/main
  sync, production/test/runtime LOC `0`, JSON/TOML, source classification,
  current public scan `1483/0`, whitespace and manifest scope.
- NOT RUN by contract: reachable history, full release baseline, live matrix,
  affected execution or successor work.

## Archive
- `openspec/changes/archive/2026-08-26-authorize-bounded-affected-release-profile-v1/`

## Related
- `openspec/changes/authorize-bounded-affected-release-profile-v1/`
- `openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md`
- `openspec/board/4.done/implement-bounded-release-semantic-scheduler-v1.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: exact affected-profile authorization is synchronized and
archived; successor and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-affected-release-profile-v1`

### Why
Published integration order requires a separate exact authorization after the
dormant scheduler is published and before affected activation exists.

### Goal
Опубликовать bounded docs-only affected-profile authorization, сохранив
successor и production activation отсутствующими.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact source, object, reference, LOC, selector, activation, authority,
  canonical-CI, dormancy and review contracts pass while successor is absent.

### Depends On
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/authorize-bounded-affected-release-profile-v1/`

## Log
- 2026-08-26 created from exact published scheduler implementation HEAD;
  affected successor absent and no executable or runtime evidence imported.
- 2026-08-26 FF created one apply-ready same-slug change; strict target/all,
  exact object/reference/lineage, JSON/TOML, current public scan and whitespace
  checks passed. No history/full/affected/live work ran.
- 2026-08-26 DO synchronized three release-CI requirements, archived the
  same-slug change and retained production/test/runtime LOC `0`. Successor,
  review, commit and push remain absent.
- 2026-08-26T12:40:25Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
