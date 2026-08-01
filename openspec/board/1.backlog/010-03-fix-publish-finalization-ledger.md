# Исправить publish finalization и ledger model

## Status
1.backlog

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
- none yet

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
- После `010-02` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z карточка выделена из двух consumer postmortems.
