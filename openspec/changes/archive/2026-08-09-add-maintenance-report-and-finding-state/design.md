## Context

`060-02` опубликовал deterministic `bin/changerail-maintenance scan --json`,
`changerail.maintenance-scan-report.v1` и
`changerail.maintenance-detector-result.v1`. Этот scan report является raw
detector contract: finding `id`, `code`, `message`, optional paths и `evidence`
приходят от detector-а или adapter-а.

Новый lifecycle layer должен быть отдельным source of truth для agents,
schedulers и metrics. Он нормализует только complete schema-valid scan output,
создает stable identity, отделяет material evidence changes и хранит runtime
continuity только под ignored `.runtime/changerail/maintenance/`.

## Goals / Non-Goals

**Goals:**
- Опубликовать `changerail.maintenance-report.v1` и runtime state schema.
- Стабилизировать finding identity через canonical JSON material.
- Отделить `fingerprint` от `evidence_fingerprint`.
- Обновлять `first_seen` только из explicit restored/written state.
- Fail closed при corrupt state, unsupported state version, unsafe paths или
  secret-like evidence.

**Non-Goals:**
- Не менять существующий `changerail.maintenance-scan-report.v1`.
- Не добавлять LLM triage или scheduler.
- Не создавать tracked cards или baseline records; это следующий change.
- Не сохранять raw detector output в tracked files.

## Decisions

1. `scan` остается raw contract, новый CLI subcommand называется `report`.
   `bin/changerail-maintenance report --json` запускает scan, валидирует scan
   report и печатает один lifecycle report в stdout. Alternative: расширить
   `scan`; отклонено, потому что existing scan schema id уже зафиксирован.
2. Runtime continuity хранится в
   `.runtime/changerail/maintenance/state.json`; запись требует
   `--write-state`. Без восстановленного state `first_seen` равен текущему
   observation timestamp, и report явно не заявляет continuity. Alternative:
   хранить continuity в tracked baseline; отклонено, потому что `first_seen`
   является mutable runtime evidence.
3. `fingerprint` считается как `sha256:<hex>` от canonical JSON с
   `identity_version`, detector result id, rule/code и normalized subject.
   `message`, `severity`, `evidence`, timestamps и workspace root исключены.
4. `evidence_fingerprint` считается отдельно от canonical sanitized material
   evidence. Evidence может измениться без изменения finding identity.
5. Sanitation выполняется до lifecycle output. Unknown absolute paths,
   traversal paths, backslash paths и secret-like values в evidence приводят к
   incomplete report с configuration diagnostic, а не к частичной нормализации.

## Risks / Trade-offs

- [Risk] Existing detectors may emit evidence that is useful but too raw. →
  Mitigation: lifecycle output stores compact sanitized evidence refs/material,
  while raw logs stay indirect runtime references outside tracked payload.
- [Risk] Ephemeral runners can lose `first_seen`. → Mitigation: report metadata
  says whether state was restored; docs/card evidence states continuity limits.
- [Risk] New schema is broad enough to overfit current detectors. →
  Mitigation: keep producer scan schema unchanged and normalize through a
  smaller lifecycle finding shape.

## Migration Plan

Add schemas and CLI behavior without changing default `scan`. Existing users
continue to receive the same scan report. New consumers can opt into:

```bash
bin/changerail-maintenance report --json
bin/changerail-maintenance report --json --write-state
```

Rollback removes the new command and schemas without invalidating previous
scan reports.

## Open Questions

- none
