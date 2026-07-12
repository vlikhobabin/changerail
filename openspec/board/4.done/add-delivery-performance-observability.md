# Добавить performance observability для delivery runner-а

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `openspec/changes/archive/2026-07-12-add-delivery-performance-contract/`
- `openspec/changes/archive/2026-07-12-capture-delivery-run-performance/`
- `openspec/changes/archive/2026-07-12-report-delivery-performance-metrics/`

## Verify
- 2026-07-12T20:03:08Z `./bin/openspec validate add-delivery-performance-contract --strict` passed.
- 2026-07-12T20:03:08Z `./bin/openspec validate capture-delivery-run-performance --strict` passed.
- 2026-07-12T20:03:08Z `./bin/openspec validate report-delivery-performance-metrics --strict` passed.
- 2026-07-12T20:03:08Z `./bin/openspec validate --all --strict` passed with 16 items.
- 2026-07-12T20:03:08Z `git diff --check` passed for tracked diffs.
- 2026-07-12T20:03:08Z explicit untracked artifact whitespace scan passed.
- 2026-07-12T20:14:41Z `python3 scripts/smoke-delivery-runner.py` passed.
- 2026-07-12T20:14:41Z `python3 scripts/smoke-delivery-metrics.py` passed.
- 2026-07-12T20:14:41Z `python3 scripts/smoke-contract-schemas.py` passed.
- 2026-07-12T20:14:41Z `./bin/openspec validate --all --strict` passed with 13 items.
- 2026-07-12T20:14:41Z `git diff --check` passed.
- 2026-07-12T20:14:41Z `python3 scripts/public-surface-scan.py` passed
  `(440 files scanned, 0 findings)`.

## Archive
- `openspec/changes/archive/2026-07-12-add-delivery-performance-contract/`
- `openspec/changes/archive/2026-07-12-capture-delivery-run-performance/`
- `openspec/changes/archive/2026-07-12-report-delivery-performance-metrics/`

## Related
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `schemas/changerail-delivery-run.schema.json`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`
- `openspec/changes/archive/2026-07-12-add-delivery-performance-contract/`
- `openspec/changes/archive/2026-07-12-capture-delivery-run-performance/`
- `openspec/changes/archive/2026-07-12-report-delivery-performance-metrics/`

## Result
implemented; awaiting independent review and publish

Published reviewed payload as `1dd8fa0`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `add-delivery-performance-contract`

### Why
Сначала нужен стабильный public contract для новых performance fields, иначе
runner и metrics будут расходиться в названиях полей и optional semantics.

### Goal
Описать schema/spec/docs для `changerail.delivery-run.v1` performance summary и
usage breakdown, включая обязательные и best-effort поля.

### Scope
- Schema delta для optional `performance` и расширенного `usage`.
- Contract docs для timing/usage semantics и runtime-only nature.
- OpenSpec requirements для delivery-run contract и observability.

### Acceptance
- `schemas/changerail-delivery-run.schema.json` принимает performance summary и
  usage breakdown без ослабления required base fields.
- Contract docs объясняют mandatory vs best-effort timing/usage fields.
- OpenSpec delta specs валидируются strict mode.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-add-delivery-performance-contract/`

## Change 2: `capture-delivery-run-performance`

### Why
Контракт полезен только если runner пишет измеримые данные во время child run,
пока доступны observed timestamps и streaming order.

### Goal
Научить delivery runner сохранять event timeline или equivalent summary с
command durations, event counts, slow commands и доступной review/publish
latency.

### Scope
- Runner parsing/aggregation для child JSONL stream.
- Status update with performance summary.
- Focused runner smoke for fake child command lifecycle events.

### Acceptance
- Fake child JSONL с command started/completed events дает ненулевые или
  измеримые command durations в runtime status.
- Runner status содержит wall time, command execution count, agent message count,
  slowest commands и terminal outcome timing when available.
- Existing runner safety-stop behavior remains covered.

### Depends On
- `add-delivery-performance-contract`

### Related
- `openspec/changes/archive/2026-07-12-capture-delivery-run-performance/`

## Change 3: `report-delivery-performance-metrics`

### Why
Оператору нужен быстрый ответ из metrics output, а не ручной анализ status и
review history.

### Goal
Показать performance summary, token breakdown и review-cycle timeline в
`bin/changerail-delivery-metrics` text/CSV output.

### Scope
- Metrics derived totals and optional usage breakdown rendering.
- Slow-command and review timeline output from structured runtime records.
- Smoke coverage for metrics output and unknown optional fields.

### Acceptance
- Metrics выводит `total_tokens`, derived from input/output when needed.
- Metrics показывает cached input, uncached input, output и reasoning tokens
  when available, иначе `unknown`.
- Metrics показывает slow-command summary и review-cycle timeline без free-text
  log scraping.

### Depends On
- `add-delivery-performance-contract`
- `capture-delivery-run-performance`

### Related
- `openspec/changes/archive/2026-07-12-report-delivery-performance-metrics/`

## Log
- 2026-07-12T18:35:00Z card created after observing that two runner-delivered
  cards required manual runtime-log analysis to explain 40-100 minute delivery
  times.
- 2026-07-12T19:59:34Z decomposed into three ordered OpenSpec changes and moved
  to `2.todo`.
- 2026-07-12T20:03:08Z OpenSpec artifacts validated and card moved to
  `3.inprogress` for delivery.
- 2026-07-12T20:14:41Z implemented, verified and archived all three card-owned
  OpenSpec changes; card remains in `3.inprogress` for independent review.
- 2026-07-12T20:24:47Z publish finalized card into `4.done` with commit `1dd8fa0` and push status `pending`.
