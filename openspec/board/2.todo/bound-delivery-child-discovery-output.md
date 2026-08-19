# Ограничить discovery output и token amplification delivery child

## Status
2.todo

## Owner
ChangeRail

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- Field-validation single-card delivery от 2026-08-18 на large generated-source
  consumer.
- `bin/changerail-delivery-runner`
- `skills/changerail-deliver/SKILL.md`
- `schemas/changerail-delivery-run.schema.json`

## Summary
Успешный supervised run сообщил более 12 млн input tokens и сохранил около
2.6 MB child JSONL. Два широких `rg` по generated source вернули примерно
650-850 KB каждый и завершились exit 130 после output truncation. Большой вывод
не дал надежного отрицательного доказательства, но многократно увеличил context
и стоимость последующих шагов.

Active-run self-ingestion уже закрыт отдельной runtime boundary. Нужен более
общий bounded discovery/output contract: child должен получать полезное
сводное доказательство, а runner должен позволять обнаружить command-output
amplification без чтения raw logs вручную.

## Acceptance
- Deliver skill требует начинать discovery с scoped paths, `rg -l`, counts или
  bounded excerpts и запрещает использовать truncated exit-130 output как
  доказательство отсутствия/наличия implementation.
- Runner performance summary записывает для command events bounded output-byte
  metadata и отмечает превышение документированного per-command threshold, не
  копируя raw output в `status.json`.
- Aggregate status различает command failure, runner truncation и успешный
  bounded result, когда Codex JSONL предоставляет достаточные поля.
- Operator-facing summary показывает top oversized commands в sanitized форме
  и дает remediation, не раскрывая source content или secrets.
- Исследуется возможность передать child explicit discovery budget/policy без
  shell interception и без зависимости от конкретной codebase language.
- Synthetic smoke генерирует oversized command output и доказывает bounded
  status size, correct byte accounting и отсутствие raw payload.
- Документируется связь output size, cached/uncached token metrics и ситуация,
  когда token usage недоступен.
- Изменение не удаляет ignored raw stdout/stderr evidence и не делает его
  committable.

## Non-Goals
- Универсальный shell sandbox или перехват всех команд агента.
- Удаление raw runtime evidence до завершения retention policy.
- Жесткий один threshold для всех repository sizes без измерений.

## Change Set
- `bound-delivery-discovery-policy`
- `record-delivery-command-output-metadata`
- `report-oversized-delivery-output`

## Verify
- `./bin/openspec validate "bound-delivery-discovery-policy" --strict`
- `./bin/openspec validate "record-delivery-command-output-metadata" --strict`
- `./bin/openspec validate "report-oversized-delivery-output" --strict`
- `./bin/openspec validate --all --strict`
- `git diff --check`

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `skills/changerail-deliver/SKILL.md`
- `scripts/smoke-delivery-runner.py`
- `schemas/changerail-delivery-run.schema.json`
- `openspec/specs/changerail-delivery-observability/spec.md`
- `openspec/changes/bound-delivery-discovery-policy/`
- `openspec/changes/record-delivery-command-output-metadata/`
- `openspec/changes/report-oversized-delivery-output/`

## Result
not started

## Next
- `$changerail-do openspec/board/2.todo/bound-delivery-child-discovery-output.md`

## Change 1: `bound-delivery-discovery-policy`

### Why
Delivery child agents need a bounded discovery contract before broad generated
source output can amplify context and cost.

### Goal
Make delivery skills and runner launch handoff require scoped discovery,
bounded excerpts and inconclusive handling for truncated output.

### Scope
- Update delivery skill and shared methodology guidance.
- Add runner child discovery budget/policy handoff.
- Keep the policy generic, public-safe and independent of shell interception.

### Acceptance
- Deliver skill requires scoped paths, `rg -l`, counts or bounded excerpts
  before broad content searches.
- Truncated command output, including exit-130 truncation, is documented as
  inconclusive for implementation presence/absence claims.
- Runner-launched children receive a compact discovery budget/policy.
- Raw ignored stdout/stderr evidence remains retained and non-committable.

### Depends On
- none

### Related
- `openspec/changes/bound-delivery-discovery-policy/`

## Change 2: `record-delivery-command-output-metadata`

### Why
Supervisors need compact machine-readable evidence that command output exceeded
safe bounds without manually reading raw child JSONL or stdout/stderr logs.

### Goal
Extend runner status and schema contracts with bounded command output metadata,
threshold flags and command result/truncation classification.

### Scope
- Add optional per-command stdout/stderr byte metadata.
- Record threshold-exceeded and truncation classification when structured child
  events provide enough fields.
- Validate the new fields through `changerail.delivery-run.v1` without breaking
  legacy records.

### Acceptance
- Runner performance summary records bounded output-byte metadata for command
  events.
- `status.json` distinguishes process failure, runner truncation and successful
  bounded command result when structured fields are available.
- Raw command output is not copied into `status.json`.
- Schema smoke covers valid metadata, legacy records and raw payload rejection.

### Depends On
- `bound-delivery-discovery-policy`

### Related
- `openspec/changes/record-delivery-command-output-metadata/`

## Change 3: `report-oversized-delivery-output`

### Why
Operators need a concise sanitized summary of oversized commands and
remediation, plus metrics/docs that explain output size beside token usage.

### Goal
Expose oversized-output diagnostics in runner summaries and metrics, backed by
synthetic smoke coverage.

### Scope
- Print top oversized commands in sanitized operator-facing output.
- Extend metrics text/JSON/CSV output and docs with output amplification fields.
- Add synthetic oversized-output smoke proving byte accounting, bounded status
  size and no raw payload copy.

### Acceptance
- Operator-facing summary shows top oversized commands and remediation without
  source content or secrets.
- Metrics distinguish output byte metadata from cached/uncached token usage and
  render unavailable fields as `unknown`.
- Synthetic smoke generates oversized command output and proves bounded
  `status.json`, correct byte accounting and ignored raw evidence retention.

### Depends On
- `record-delivery-command-output-metadata`

### Related
- `openspec/changes/report-oversized-delivery-output/`

## Log
- 2026-08-18T17:39:30Z создана после supervised run, где delivery завершился,
  но unbounded discovery output вызвал непропорциональную token amplification.
- 2026-08-19T06:22:24Z decomposed by `$chrl-ff` into three ordered OpenSpec
  changes and moved to `2.todo`.
