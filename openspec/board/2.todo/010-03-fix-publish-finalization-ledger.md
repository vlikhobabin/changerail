# Исправить publish finalization и ledger model

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`010-core-release-contracts`

## Series Index
`03`

## Source
- Два независимых consumer delivery run подтвердили self-invalidating tracked
  publish metadata.

## Summary
Убрать exact final commit hash и mutable push state из tracked done-card,
разделить payload и published commits в ignored manifest и сделать
card-only finalization whitespace-safe.

## Acceptance
- Tracked done-card не содержит собственный final commit hash.
- Push-enabled flow не оставляет `push status pending` в tracked результате.
- Ignored manifest различает `payload_commit` и `published_commit` и хранит
  final remote/branch/status/timestamp.
- После board move manifest содержит final `card.path` и `card.status`.
- `finalize-card` не создает blank line at EOF или иной `git diff --check`
  defect.
- Local bare-remote regression smoke проходит commit, finalize, amend, push и
  publish-update без stale metadata.

## Scope
- Delivery manifest schema/helper.
- `changerail-pub` contract и publish/finalization docs.
- Focused finalization smoke и migration note.

## Non-Goals
- Полная scope reconciliation: карточка `010-04`.
- Remote retry/resume: карточка `020-03`.

## Depends On
- `010-02-establish-supported-python-runtime`

## Implementation Notes
- Tracked card должна содержать только стабильный outcome; exact pushed commit
  доступен из Git history и ignored ledger.
- Финализация после `go` не может менять substantive reviewed payload.

## Change Set
- `fix-publish-finalization-ledger` (planned)

## Change 1: `fix-publish-finalization-ledger`

### Why
Tracked done-card metadata не может заранее содержать собственный final commit
hash, а mutable push state в карточке делает published result self-invalidating.

### Goal
Разделить stable tracked finalization и ignored publish ledger так, чтобы scoped
publish не оставлял stale или impossible metadata в board card.

### Scope
- Delivery manifest schema/helper.
- `changerail-pub` contract и publish/finalization docs.
- Focused finalization regression smoke с local bare remote.

### Acceptance
- Tracked done-card не содержит собственный final commit hash.
- Push-enabled flow не оставляет `push status pending` в tracked результате.
- Ignored manifest различает `payload_commit` и `published_commit` и хранит
  final remote/branch/status/timestamp.
- После board move manifest содержит final `card.path` и `card.status`.
- `finalize-card` не создает blank line at EOF или иной `git diff --check`
  defect.
- Local bare-remote regression smoke проходит commit, finalize, amend, push и
  publish-update без stale metadata.

### Depends On
- `establish-supported-python-runtime`

### Related
- `openspec/changes/fix-publish-finalization-ledger/`

## Verify
- Focused publish finalization smoke с local bare remote.
- Manifest schema smoke.
- `git show --check --oneline HEAD` в fixture.
- Release baseline и public-surface scan.

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `scripts/changerail_delivery_manifest.py`
- `schemas/changerail-delivery-manifest.schema.json`
- `skills/changerail-pub/SKILL.md`

## Result
not started

## Next
- Выполнить через series `010` runner plan после `010-02`.

## Log
- 2026-08-01T15:07:29Z карточка выделена из двух consumer postmortems.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для runner delivery.
