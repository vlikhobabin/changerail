## 1. Decision-Only Investigation

- [x] 1.1 Обновить investigation card полным набором selected decisions для
  exact child argv/no-push, replay-derived repair usage, recursive
  `resume_from` ownership и unique canonical Git workspace roots.
- [x] 1.2 Зафиксировать отсутствие дополнительного versioned wire field:
  residual integrity использует существующие unpublished v1 candidate fields,
  а cross-record checks выполняет production semantic validator.
- [x] 1.3 Зафиксировать atomic successor
  `replace-phase-routed-resume-integrity-boundary`, отдельный authorization
  `authorize-bounded-phase-routed-resume-integrity-payload`, все initial,
  review/published paths и exact six-field authorization object с ceiling 500
  и protocol allowance `true`.
- [x] 1.4 Связать cycle-3 R1-R5 с connected production matrix, где каждый
  negative имеет passing canonical base, isolated mutation, exact rejection
  reason и `model_launch_delta: 0`, а positive nested resume достигает DO
  attempt 4 после двух FF `BLOCKED` hops.
- [x] 1.5 Подтвердить scoped diff, что decision payload не меняет production
  code, schemas, tests, CLI, public runtime docs или runtime behavior и не
  создает successor/authorization cards.

## 2. Spec Sync And Archive

- [x] 2.1 Синхронизировать delta requirement
  `Phase-routed resume-integrity rescue investigation decision` в
  `openspec/specs/changerail-delivery-runner/spec.md` только во время apply
  phase.
- [x] 2.2 Архивировать
  `decide-phase-routed-resume-integrity-rescue` после successful validation и
  обновить только investigation card archive/result/related metadata.
- [x] 2.3 Оставить создание exact replacement и authorization cards после
  fresh independent `GO` и publish этого investigation; текущий change их не
  материализует.

## 3. Verification

- [x] 3.1 Запустить `bin/openspec validate
  "decide-phase-routed-resume-integrity-rescue" --strict` до sync/archive.
- [x] 3.2 После spec sync запустить `bin/openspec validate
  "changerail-delivery-runner" --strict` и `bin/openspec validate --all
  --strict`.
- [x] 3.3 Запустить `python3 scripts/public-surface-scan.py` и подтвердить, что
  tracked decision artifacts не содержат private paths, runtime evidence или
  secrets.
- [x] 3.4 Запустить `python3 -m json.tool .mcp.json` и TOML parse
  `.codex/config.toml` согласно repository baseline.
- [x] 3.5 Запустить `git diff --check` и отдельный whitespace scan для новых
  untracked artifacts до их учета manifest/staging scope.
- [x] 3.6 Перед review запустить
  `bin/changerail-delivery-manifest scope-check <manifest> --workspace .
  --target working-tree --json` и подтвердить отсутствие missing, extra или
  mismatched paths.
