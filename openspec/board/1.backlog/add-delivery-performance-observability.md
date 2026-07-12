# Добавить performance observability для delivery runner-а

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Тестовый пакетный запуск ChangeRail runner-а 2026-07-12:
  `runner-test-01-harden-contracts`,
  `runner-test-02-protect-public-data`,
  `runner-test-02-protect-public-data-resume`.
- `.runtime/changerail/delivery-runs/*/status.json`
- `.runtime/changerail/delivery-runs/*/stdout.jsonl`
- `.runtime/changerail/reviews/*.history.json`
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `docs/changerail-contracts.md`

## Summary
Сделать длительность delivery-run-ов объяснимой из machine-readable runtime
evidence. Сейчас runner записывает общий wall time и usage, но не сохраняет
структурированную разбивку по child JSONL events, command durations,
verification overhead, review-cycle pauses и token totals, поэтому после
длинного прогона приходится вручную разбирать `stdout.jsonl`.

На двух тестовых карточках delivery занял десятки минут: первая карточка
содержала 3 OpenSpec changes и дошла до third review cycle, вторая содержала 5
OpenSpec changes, 71 changed path и также дошла до third review cycle. Локальные
проверки показали, что отдельные gates занимают секунды или десятки секунд, а
основной множитель времени находится в размере карточки, количестве LLM/tool
итераций и repeated review/fix cycles. Эти выводы должны быть доступны из
обычного metrics/status output без ad hoc Python анализа runtime logs.

## Findings
- `status.json` содержит общий `started_at`/`ended_at`, но не содержит
  breakdown по фазам, tool calls, command counts, slow commands и review cycles.
- `stdout.jsonl` содержит Codex item events, но runner пишет его raw stream без
  runner-observed timestamps; длительность отдельных command executions нельзя
  надежно посчитать после факта.
- `bin/changerail-delivery-metrics` сейчас не показывает `total_tokens` для runs,
  где status содержит только `input_tokens` и `output_tokens`.
- Metrics не показывает cached/non-cached input, output и reasoning token
  breakdown, хотя это важно для понимания LLM-cost и latency drivers.
- Review-cycle history содержит `reviewed_at` и findings, но metrics не
  показывает review cycle count, first review latency, time between cycles и
  final-go cycle.
- Нет summary, который отделяет verification overhead от LLM/review/fix
  overhead и помогает решить, нужно ли резать карточки меньше.

## Acceptance
- Delivery runner сохраняет machine-readable event timeline или equivalent
  summary для child JSONL stream с runner-observed timestamps, event ids,
  command start/end, command duration и terminal outcome.
- `status.json` содержит агрегированную performance summary: wall time,
  command execution count, agent message count, file change count, slowest
  commands, review cycle count, first-review latency, time-to-final-go и publish
  latency, когда эти данные доступны.
- `bin/changerail-delivery-metrics` корректно считает и выводит `total_tokens`
  из `input_tokens + output_tokens`, а также показывает cached input, uncached
  input, output и reasoning tokens при наличии данных.
- Metrics умеет показать per-run slow-command summary и review-cycle timeline
  без скрейпинга свободного текста stdout/stderr.
- Runtime artifacts остаются ignored state; tracked payload получает только
  schema/docs/scripts/tests изменения.
- Contract docs описывают, какие timing и usage поля являются best-effort, а
  какие обязательны для `changerail.delivery-run.v1`.
- Smoke покрывает: fake child с несколькими started/completed command events
  получает измеримые durations; metrics выводит total tokens и review-cycle
  count; отсутствующие optional timing fields отображаются как `unknown`.
- Финальная verification evidence включает focused smoke для runner/metrics,
  OpenSpec strict validation, `git diff --check` и public-surface scan.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `schemas/changerail-delivery-run.schema.json`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`

## Result
not started

## Next
- Split into OpenSpec changes for runner event timing, metrics usage totals and
  review-cycle timing summary.

## Log
- 2026-07-12T18:35:00Z card created after observing that two runner-delivered
  cards required manual runtime-log analysis to explain 40-100 minute delivery
  times.
