## 1. Decision-Only Investigation

- [x] 1.1 Сверить investigation card, proposal, design и delta spec: exact
  blocker, reviewed tree/fingerprint, rescue budget `2/2`, successor id и
  public-safe lineage MUST совпадать без machine-local runtime evidence.
- [x] 1.2 Подтвердить selected minimal boundary, measured baseline 299,
  incremental forecast 60..100, cumulative forecast 359..399 и hard ceiling
  400; source classification и regression floor не менять.
- [x] 1.3 Зафиксировать exact future authorization id/paths и six-field object
  с `production_loc_ceiling: 400` и
  `allow_new_authority_or_wire_protocol: false`, сохранив текущий source как
  `Published investigation authorization: none`.
- [x] 1.4 Проверить scoped diff: production code, skills/runtime behavior,
  schemas, workflows, authorization/successor cards, release tag/assets и
  publication mutation в этом change отсутствуют.

## 2. Spec Sync And Archive

- [x] 2.1 Синхронизировать delta requirement `First stable post-commit resume
  boundary investigation decision` в
  `openspec/specs/changerail-release-discipline/spec.md` только во время apply
  phase и строго провалидировать capability.
- [x] 2.2 Архивировать
  `decide-post-commit-release-resume-entry-boundary` после successful
  validation; обновить card archive/result/related metadata и оставить future
  authorization/successor implementation за отдельными sessions.
- [x] 2.3 Сформировать ignored delivery manifest только для investigation
  payload и выполнить working-tree scope reconciliation перед review handoff.

## 3. Verification

- [x] 3.1 Запустить `bin/openspec validate
  "decide-post-commit-release-resume-entry-boundary" --strict` до sync/archive.
- [x] 3.2 После sync/archive запустить `bin/openspec validate
  "changerail-release-discipline" --strict` и
  `bin/openspec validate --all --strict`.
- [x] 3.3 Запустить `python3 scripts/public-surface-scan.py` и
  `python3 scripts/public-surface-scan.py --history`; подтвердить отсутствие
  private paths, runtime dumps, credentials и secrets в tracked decision
  artifacts.
- [x] 3.4 Запустить `python3 -m json.tool .mcp.json` и TOML parse
  `.codex/config.toml` согласно repository baseline.
- [x] 3.5 Запустить `git diff --check` и отдельный whitespace scan новых
  untracked artifacts до их учета manifest/staging scope.
- [x] 3.6 Перед review запустить
  `bin/changerail-delivery-manifest scope-check <manifest> --workspace .
  --target working-tree --json` и подтвердить отсутствие missing, extra или
  mismatched paths.

## 4. Same-Card Rescue R1

- [x] 4.1 Синхронно обновить card, proposal, design, archived delta и main
  release-discipline spec: future authorization-card и exact successor MUST
  обе объявить `Depends On` exact investigation id
  `investigate-post-commit-release-resume-entry-boundary`.
- [x] 4.2 Потребовать, чтобы canonical deterministic preflight проверял обе
  reciprocal dependency edges вместе с six-field authorization object и
  two-field successor reference и fail closed при missing/mismatched relation;
  ceiling `400`, protocol allowance `false`, production classification и
  verification floor сохранить без изменений.
- [x] 4.3 Повторить docs/OpenSpec/public/config/whitespace verification,
  обновить ignored manifest без удаления cycle 1 `NO-GO` history и получить
  normalized `ready-for-llm-review` handoff для same-card rescue attempt 1.
