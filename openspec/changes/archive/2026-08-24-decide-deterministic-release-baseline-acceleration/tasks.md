## 1. Decision Evidence

- [x] 1.1 Подтвердить published history/baseline timestamps и bounded inventory
  counts без запуска полного release baseline или повторного history scan;
  retained index extraction фиксирует 627.163 s и 1810.799 s.
- [x] 1.2 Подтвердить standalone timing, case/workspace counts и отсутствие
  persistent reuse для текущих review-preflight и delivery-runner smoke.
- [x] 1.3 Проверить, что design точно задаёт path-sensitive content key, fresh
  reachability, policy/input invalidation, batch object I/O и corruption
  recovery без whole-baseline receipt.
- [x] 1.4 После cycle-1 NO-GO создать и validate card-owned ignored evidence
  index с exact command/output/duration для prior extraction, inventory,
  object-I/O microbenchmark и fresh cold/warm smoke; history и полный baseline
  не повторять.

## 2. Successor Boundaries

- [x] 2.1 Зафиксировать первым successor scope history scanner с parity,
  path/rename, corruption, invalidation, cold/warm timing и per-step baseline
  instrumentation acceptance.
- [x] 2.2 Зафиксировать вторым successor scope smoke process isolation,
  bounded jobs/timeouts, deterministic aggregation, crash/timeout negatives и
  sequential/parallel timing acceptance.
- [x] 2.3 Подтвердить, что decision не создаёт successor cards, не меняет
  production scripts/tests/schemas/runtime и не вводит новую authority.
- [x] 2.4 Исправить current-policy path parity, потребовать frozen parent-blob
  completeness oracle с fault injection для каждого registry ID и определить
  frozen scale, host/runtime capture, sampling/variance и numeric RSS bounds.

## 3. Decision Verification

- [x] 3.1 Запустить `bin/openspec validate
  decide-deterministic-release-baseline-acceleration --strict` и
  `bin/openspec validate --all --strict`.
- [x] 3.2 Запустить `python3 scripts/public-surface-scan.py`, JSON/TOML parse и
  `git diff --check`; полный baseline и history scan для decision не запускать.
- [x] 3.3 Проверить scoped status/diff, сохранить public-safe concise outcomes и
  передать decision на fresh independent review перед публикацией.
