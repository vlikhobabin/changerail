# Добавить read-only представление текущего delivery-состояния

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Сравнение ChangeRail с Orca от 2026-08-12.
- Наблюдение за package-runner delivery от 2026-08-19: aggregate
  `status-plan` был полезен, но single-card состояние пришлось определять по
  process tree и отдельным runtime paths.
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
- `add-delivery-runtime-attention-view`

## Verify
- GREEN: `python3 -m py_compile bin/changerail-delivery-runner
  scripts/smoke-delivery-runner.py`
- GREEN: `python3 scripts/smoke-delivery-runner.py`
- GREEN: `./bin/openspec validate add-delivery-runtime-attention-view --strict`
  before archive.
- GREEN: `./bin/openspec validate --all --strict` -> 23/23 passed after
  archive.
- GREEN: `git diff --check`
- GREEN: untracked-file trailing-whitespace scan over `git ls-files --others
  --exclude-standard` -> 0 untracked paths.
- GREEN: `python3 scripts/public-surface-scan.py` -> 1086 files scanned, 0
  findings.

## Archive
- `openspec/changes/archive/2026-08-19-add-delivery-runtime-attention-view/`

## Related
- `AGENTS.shared.md`
- `docs/changerail-contracts.md`
- `docs/how-it-works.md`
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-manifest.schema.json`
- `openspec/board/4.done/support-runner-resume-after-investigation-required.md`
- `openspec/changes/archive/2026-08-19-add-delivery-runtime-attention-view/`

## Result
Implemented read-only single-card delivery status reader, docs, synced spec and
smoke coverage.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Triage Decision
- Move to `2.todo`: capability отсутствует и подтвердила ценность в реальном
  длительном package-runner delivery, а OpenSpec artifacts теперь apply-ready.
- Priority: medium. Сначала закрыть невозможность resume после
  `investigation_required`, затем улучшать operator visibility.

## Change 1: `add-delivery-runtime-attention-view`

### Why
Single-card delivery status already exists as schema-backed ignored runtime
records, but operators lack one compact read-only command to inspect a current
or blocked card without process-tree checks or ad hoc runtime path lookup.

### Goal
Add a minimal single-card `bin/changerail-delivery-runner status` command that
validates an existing `changerail.delivery-run.v1` record, prints compact
human-readable attention fields and surfaces canonical related manifest,
verdict and evidence paths without mutating runtime state.

### Scope
- Add single-card `status` CLI selection by explicit `status.json`, `--run-id`
  or latest record in the effective workspace runtime root.
- Validate selected delivery-run status before display and fail closed for
  missing, corrupt, schema-invalid or unsupported inputs.
- Derive canonical related delivery manifest, review verdict, review history
  and retained evidence paths from the validated status/card/workspace.
- Render manifest `runtime_pause_reasons[].summary` and
  `runtime_pause_reasons[].next_action` only from validated manifest structure.
- Keep `status-plan` as the aggregate queue reader and defer any common reader
  schema until a machine consumer needs it.
- Update docs and focused runner smoke coverage.

### Acceptance
- Explicit status path, `--run-id` and latest workspace selection read the
  intended single-card `changerail.delivery-run.v1` record.
- Invalid selected status records fail closed without fallback to another run.
- Human output shows card, phase, result, `updated_at`, `terminal_reason`,
  selected status path and unambiguous related runtime paths.
- Existing manifest pause `summary` and `next_action` values are shown without
  deriving guidance from raw logs, process state or free-text agent sessions.
- `--json` returns the schema-valid source status record and does not introduce
  an unschematized machine view.
- Status inspection is read-only for board files, locks, manifests, verdicts,
  evidence indexes, logs and status records.
- Focused smoke covers success, latest or run-id selection, blocked/no-go
  diagnostics, manifest pause reasons, invalid input and read-only behavior.

### Depends On
- `record-investigation-required-payload-identity`
- `resume-investigation-required-single-card`
- `support-investigation-required-queue-recovery`

### Related
- `openspec/changes/add-delivery-runtime-attention-view/`

## Log
- 2026-08-12T09:30:49Z карточка создана по итогам сравнения ChangeRail с Orca;
  scope ограничен operator visibility поверх существующих runtime records.
- 2026-08-19T14:05:00Z triage подтвердил актуальность: `status-plan` покрывает
  aggregate plan, но отдельного schema-valid single-card reader нет; карточка
  оставлена в backlog после runner resume fix.
- 2026-08-19T15:32:59Z `$chrl-ff` decomposed the story into one read-only
  single-card status/attention change and moved the card to `2.todo`.
- 2026-08-19T15:33:57Z OpenSpec validation and whitespace checks passed for
  generated artifacts and card metadata.
- 2026-08-19T19:24:55Z implemented `bin/changerail-delivery-runner status`,
  updated docs and smoke coverage, synced `changerail-delivery-runner` spec and
  archived `add-delivery-runtime-attention-view`; verification passed.
- 2026-08-19T19:48:22Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
