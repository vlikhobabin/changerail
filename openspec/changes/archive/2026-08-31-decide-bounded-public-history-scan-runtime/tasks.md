## 1. Public-safe profile

- [x] 1.1 Построить ignored public-safe synthetic Git fixture с повторяющимися blobs и измерить process/runtime growth текущего history scanner.
- [x] 1.2 Сопоставить synthetic profile с retained `canonical-history-timeout`, не копируя raw runtime или machine-specific paths в tracked artifacts.

## 2. Bounded decision

- [x] 2.1 Зафиксировать exact `HEAD` release-ref semantics, unique-blob batching, commit/path attribution и strict Git framing lifecycle.
- [x] 2.2 Зафиксировать regression matrix, ceiling 30 секунд для focused fixture, 300 секунд для clean release baseline и максимум три Git process launches.
- [x] 2.3 Назвать exact successor `implement-bounded-public-history-scan-runtime`, production LOC ceiling 300 и решение, что отдельная authorization card не требуется.

## 3. Public handoff

- [x] 3.1 Синхронизировать delta requirement в `changerail-release-ci` без изменения production scanner, baseline, CI workflow или smoke tests.
- [x] 3.2 Создать одну deliver-ready successor card с reciprocal investigation link, bounded scope и verification floor.
- [x] 3.3 Обновить investigation card результатом, verification evidence и archive handoff.

## 4. Verification

- [x] 4.1 Запустить `bin/openspec validate decide-bounded-public-history-scan-runtime --strict` и `bin/openspec validate --all --strict`.
- [x] 4.2 Запустить `python3 scripts/public-surface-scan.py`, scoped whitespace check и `git diff --check`.
- [x] 4.3 Синхронизировать main spec и архивировать completed change без изменения production files.
