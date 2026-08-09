## Why

После появления lifecycle findings сопровождающим нужен reviewable способ
accept или temporary waive известных findings, а agents нужен безопасный bridge
из findings в board cards без duplicate tracked work. Defaults должны
оставаться read-only, чтобы scans и previews не мутировали Git неожиданно.

## What Changes

- Добавить tracked `.changerail/maintenance-baseline.yaml` contract с
  отдельными `accepted` identities и `waivers`.
- Требовать для waiver owner, reason и review/expiry boundary, а expired
  waivers считать fail-open вместо подавления current findings.
- Добавить preview-first CLI surfaces `accept-baseline`, `triage` и `cards`.
- Добавить board-card bridge, который пишет только при explicit `--write`,
  сканирует все board lanes по exact marker
  `Maintenance Origin: <sha256 fingerprint>` и обновляет existing card вместо
  duplicate creation.
- Гарантировать, что card titles, summaries и evidence references используют
  только sanitized repository-relative metadata.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: добавить tracked maintenance baseline,
  waiver, triage annotation и board-card deduplication requirements.

## Impact

- `schemas/` получает public maintenance baseline и triage annotation schemas.
- `.changerail/maintenance-baseline.yaml` становится optional tracked
  reviewable baseline file.
- `scripts/changerail_repository_knowledge.py` и `bin/changerail-maintenance`
  получают preview/write lifecycle commands и board-card upsert behavior.
- Smoke fixtures покрывают baseline validation, default no-mutation, explicit
  write scope и duplicate-card prevention.
