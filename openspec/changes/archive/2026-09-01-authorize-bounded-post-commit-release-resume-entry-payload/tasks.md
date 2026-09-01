## 1. Authorization Source

- [x] 1.1 Сверить card с exact published investigation: сохранить ровно один
  six-field machine-readable object, exact investigation/successor ids и paths,
  integer ceiling `400`, boolean protocol allowance `false` и собственный
  `Depends On: investigate-post-commit-release-resume-entry-boundary`.
- [x] 1.2 Детерминированно распарсить единственную `Investigation
  authorization` JSON строку и сравнить semantic key set, types и values с
  normative object; missing, duplicated, extra или mismatched данные считать
  fail-closed blocker.
- [x] 1.3 Сохранить measured baseline `299`, forecast `359..399`, planned
  increment `<=100` и hard stop `401+`; не расширять investigated boundary и не
  менять source classification или regression floor.
- [x] 1.4 Подтвердить, что successor card не изменена и two-field
  authorization reference в неё не добавлен до публикации authorization-card;
  exact successor path/dependency/reference остаются обязательным входом
  последующего canonical preflight.

## 2. Spec Sync And Archive

- [x] 2.1 Синхронизировать ADDED requirement `First stable bounded post-commit
  resume authorization source` в
  `openspec/specs/changerail-release-discipline/spec.md` только во время apply
  phase и строго провалидировать capability.
- [x] 2.2 Архивировать
  `authorize-bounded-post-commit-release-resume-entry-payload` после successful
  validation и обновить только status/archive/result metadata этой card для
  independent review handoff.
- [x] 2.3 Сверить scoped diff: допустимы только authorization card, её OpenSpec
  artifacts/archive и синхронизированный release-discipline spec; production,
  runtime, tests, schemas, providers, credentials, workflows, successor card,
  release-card, tag/Release/assets и release mutation MUST отсутствовать.

## 3. Verification

- [x] 3.1 До sync/archive запустить `bin/openspec validate
  "authorize-bounded-post-commit-release-resume-entry-payload" --strict`.
- [x] 3.2 После sync/archive запустить `bin/openspec validate
  "changerail-release-discipline" --strict` и
  `bin/openspec validate --all --strict`.
- [x] 3.3 Запустить неизменённый
  `python3 scripts/smoke-review-preflight.py` как regression для generic
  six-field parsing и reciprocal investigation dependency fail-closed
  behavior; exact successor positive admission остаётся невозможным до
  отдельного post-publication successor update.
- [x] 3.4 Запустить `python3 scripts/public-surface-scan.py`; до public commit
  также запустить `python3 scripts/public-surface-scan.py --history` и
  подтвердить отсутствие private paths, secrets и runtime state.
- [x] 3.5 Запустить `python3 -m json.tool .mcp.json`, TOML parse
  `.codex/config.toml`, `git diff --check` и отдельный whitespace scan всех
  новых untracked card/artifact files.
- [x] 3.6 Перед review выполнить working-tree scope reconciliation по
  delivery manifest и подтвердить, что successor/release surfaces не входят в
  payload.

## 4. Fresh Review Cycle 2 Repair

- [x] 4.1 По SSH получить и обычным fast-forward merge интегрировать published
  prerequisite `e14c56db582c75bf4000ddff4c64be687fccd730`; до merge подтвердить
  нулевое пересечение его 10 paths с семью manifest paths и после merge
  сохранить exact 7-path docs/OpenSpec authorization scope.
- [x] 4.2 На новом `origin/main` повторить exact authorization semantics,
  обновлённый focused adversarial preflight smoke, strict OpenSpec,
  current/history public scans, JSON/TOML и diff/whitespace checks; сохранить
  production LOC `0`, ceiling `400` и protocol allowance `false`.
- [x] 4.3 Обновить ignored delivery manifest и cycle 1 `NO-GO` handoff без
  удаления verdict history, выполнить clean working-tree scope reconciliation
  и normalized preflight для fresh independent review cycle 2.
