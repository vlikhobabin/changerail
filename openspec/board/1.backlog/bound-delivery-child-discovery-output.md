# Ограничить discovery output и token amplification delivery child

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
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `skills/changerail-deliver/SKILL.md`
- `scripts/smoke-delivery-runner.py`
- `schemas/changerail-delivery-run.schema.json`
- `openspec/specs/changerail-delivery-observability/spec.md`

## Result
not started

## Next
- triage

## Log
- 2026-08-18T17:39:30Z создана после supervised run, где delivery завершился,
  но unbounded discovery output вызвал непропорциональную token amplification.
