## 1. Decision-Only Investigation

- [x] 1.1 Обновить investigation card однозначными решениями по
  repair budget, canonical card identity, blocked resume, aggregate runtime
  root и authority/provenance boundary.
- [x] 1.2 Привязать cycle-3 R1–R6 к exact successor regression matrix,
  в которой aggregate/resume authority проверяет production
  single-card preflight.
- [x] 1.3 Зафиксировать exact replacement
  `implement-phase-routed-delivery-authorization-boundary`, exact separate
  authorization source `authorize-bounded-phase-routed-delivery-payload`,
  production LOC ceiling 500 и protocol allowance `true`.
- [x] 1.4 Подтвердить по diff, что investigation не изменил
  production runner, schemas, smoke implementation, CLI, public runtime docs
  и runtime behavior.

## 2. Spec Sync And Archive

- [x] 2.1 Синхронизировать delta requirement в
  `openspec/specs/changerail-delivery-runner/spec.md`.
- [x] 2.2 Архивировать
  `decide-phase-routed-delivery-authorization-boundary` после успешной
  validation, не создавая и не реализуя replacement в этом
  change.

## 3. Verification

- [x] 3.1 Запустить `bin/openspec validate
  "decide-phase-routed-delivery-authorization-boundary" --strict`.
- [x] 3.2 Запустить `bin/openspec validate
  "changerail-delivery-runner" --strict` после spec sync.
- [x] 3.3 Запустить `bin/openspec validate --all --strict`.
- [x] 3.4 Запустить `python3 scripts/public-surface-scan.py`.
- [x] 3.5 Запустить `git diff --check` и отдельный trailing-whitespace
  scan для untracked artifacts.
- [x] 3.6 Перед review запустить
  `bin/changerail-delivery-manifest scope-check <manifest> --workspace . --target working-tree --json`
  и подтвердить decision-only scope.
