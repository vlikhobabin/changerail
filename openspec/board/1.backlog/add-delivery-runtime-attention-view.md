# Добавить read-only представление текущего delivery-состояния

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Сравнение ChangeRail с Orca от 2026-08-12.
- [Orca CLI guide](https://github.com/stablyai/orca/blob/main/skill-guides/orca-cli.md)
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-manifest.schema.json`
- `docs/how-it-works.md`

## Summary
ChangeRail уже сохраняет machine-readable single-card run status, aggregate
plan status, review verdicts, manifest checkpoints и pause reasons с
`next_action`, но оператору недостает одного компактного read-only входа для
ответа на вопросы: что сейчас выполняется, почему delivery остановлен и где
находится каноническое evidence для продолжения.

Добавить минимальное status/attention представление поверх существующих
runtime contracts. Не создавать новый scheduler, daemon, message bus или
управление агентами: источник истины остается в уже существующих ignored JSON
records.

## Acceptance
- `bin/changerail-delivery-runner` предоставляет read-only команду для чтения
  single-card `changerail.delivery-run.v1` status по explicit path, `run_id`
  или последней записи текущего workspace.
- Команда валидирует входной status по существующей schema и fail-closed
  сообщает о missing, corrupt или unsupported record.
- Компактный human-readable output показывает card, phase, result,
  `updated_at`, `terminal_reason` и repository-relative пути к связанным
  manifest, review verdict и retained evidence, когда они однозначно
  разрешаются.
- Когда delivery manifest содержит актуальный `runtime_pause_reasons`, output
  показывает существующие `summary` и `next_action`, не выводя их из raw log
  или свободного текста agent session.
- Plan status остается доступен через существующий `status-plan`; triage должен
  решить, нужен ли один общий reader для single-card и plan records без
  изменения их source schemas.
- JSON mode возвращает schema-valid source record или минимальный view, для
  которого необходимость отдельного публичного schema contract доказана в
  design; human-only convenience не должен ослаблять machine-readable path.
- Runtime paths, logs, verdicts и manifests остаются ignored; команда не
  изменяет board, process state, locks, manifests или status records.
- Focused smoke покрывает successful read, latest selection, blocked/no-go
  diagnostics, manifest pause reason и corrupt/unsupported input.

## Non-Goals
- Desktop, mobile или browser UI.
- Live `ask/reply`, agent inbox, threaded messaging или prompt injection в
  работающий child process.
- Запуск, остановка или автоматическое восстановление процессов.
- Новый worker lifecycle, scheduler, worktree manager или Orca backend.
- Автоматическое признание старой `RUNNING` записи завершенной только по
  возрасту или отсутствию PID.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `AGENTS.shared.md`
- `docs/changerail-contracts.md`
- `docs/how-it-works.md`
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-manifest.schema.json`

## Result
not started

## Next
- triage

## Change Plan Notes
Перед переводом в `2.todo` выбрать минимальную CLI-форму и проверить, можно ли
полностью переиспользовать существующие status/manifest schemas. Предпочтение
следует отдать одному read-only change без нового runtime writer или daemon.

## Log
- 2026-08-12T09:30:49Z карточка создана по итогам сравнения ChangeRail с Orca;
  scope ограничен operator visibility поверх существующих runtime records.
