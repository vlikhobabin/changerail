## Why

Обязательный release baseline уже сохраняет строгий fail-closed gate, но три
его этапа повторяют большую долю неизменной работы. Published evidence фиксирует
627.163 s для standalone history scan и 1810.799 s для последующего baseline; на текущих
92 reachable commits scanner делает 102706 отдельных commit/path чтений, а два
крупных smoke выполняют десятки изолируемых fixtures последовательно.

## What Changes

- Принять decision о content-addressed, path-sensitive history scanning через
  batch Git object I/O и fail-closed policy/input invalidation.
- Принять decision о process-isolated параллельных case groups для
  `smoke-review-preflight.py` и `smoke-delivery-runner.py` с bounded jobs,
  per-case timeout и детерминированной parent-side агрегацией.
- Зафиксировать parity, negative, corruption, invalidation и timing acceptance,
  не разрешая пропуск команд или шагов полного baseline.
- Разделить последующую реализацию на два ordered successor scopes: сначала
  history scanner, затем smoke parallelization. Этот decision change не создаёт
  successor cards и не меняет production scripts, tests, schemas или runtime.
- Не вводить reusable whole-baseline receipt, publish authority или иной новый
  authority/wire protocol.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: обязательные history и smoke gates сохраняются, но
  получают fail-closed content reuse, bounded isolated concurrency и
  детерминированную агрегацию.

## Impact

Decision затрагивает будущую реализацию в `scripts/public-surface-scan.py`,
`scripts/smoke-review-preflight.py` и `scripts/smoke-delivery-runner.py`, а также
focused parity/timing fixtures. `scripts/run-release-baseline.py` продолжает
вызывать те же обязательные команды; consumer projects, credentials, network и
public wire schemas не затрагиваются.
