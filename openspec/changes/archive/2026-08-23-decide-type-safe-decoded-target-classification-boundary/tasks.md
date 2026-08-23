## 1. Decision-Only Investigation

- [x] 1.1 Проверить, что investigation card содержит exact ordered algorithm:
  pair-preserving decode, linear typed hints, one-target selection,
  duplicate/shape/type validation, materialization, semantic checks и review
  eligibility.
- [x] 1.2 Проверить total/non-throwing contract для любого JSON value и явный
  запрет hashing/set membership, path или relation use для unvalidated values
  четырех identity fields.
- [x] 1.3 Проверить полный connected cross-product четырех identity keys,
  scalar/container values и alternate-escaped duplicate keys в обоих pair
  orders, включая array/object-first rows.
- [x] 1.4 Проверить candidate/shape/semantic groups и exact structured oracle:
  fresh canonical base, isolated mutation, exact exit/outcome/status/detail,
  separate owned semantic-check и semantic-review-dispatch counters,
  `model_launch_delta: 0` и отсутствие uncaught exception.
- [x] 1.5 Проверить единственный next item
  `authorize-type-safe-phase-routed-resume-integrity-payload`, reciprocal
  relations, its <=300 parser production LOC boundary, exact six-field object
  with downstream ceiling 500/protocol `true` и exact two-field successor
  reference.
- [x] 1.6 Подтвердить scoped diff: production code, schemas, tests, CLI, public
  runtime docs/runtime behavior, rejected source/rescue payloads, authorization
  card и implementation successor не изменены и не созданы.

## 2. Spec Sync And Archive

- [x] 2.1 Синхронизировать delta requirement `Type-safe decoded authorization
  target classification decision` в
  `openspec/specs/changerail-contracts/spec.md` только во время apply phase.
- [x] 2.2 Архивировать
  `decide-type-safe-decoded-target-classification-boundary` после successful
  validation и обновить только investigation card archive/result/related
  metadata.
- [x] 2.3 Оставить создание
  `authorize-type-safe-phase-routed-resume-integrity-payload` и
  `replace-phase-routed-resume-integrity-boundary` после fresh independent
  review и publish этой investigation; не использовать rejected payloads как
  publish source.
- [x] 2.4 Оставить карточку в `3.inprogress` для `$changerail-review`; review
  получает fresh `GO`, а GO требуется только следующему `$changerail-pub` и
  finalization.

## 3. Verification

- [x] 3.1 Запустить `bin/openspec validate
  decide-type-safe-decoded-target-classification-boundary --strict` до
  sync/archive.
- [x] 3.2 После spec sync запустить `bin/openspec validate
  changerail-contracts --strict` и `bin/openspec validate --all --strict`.
- [x] 3.3 Запустить `python3 scripts/public-surface-scan.py` и подтвердить, что
  decision artifacts не содержат private paths, runtime evidence или secrets.
- [x] 3.4 Запустить `python3 -m json.tool .mcp.json` и TOML parse
  `.codex/config.toml` согласно repository baseline.
- [x] 3.5 Запустить `git diff --check` и отдельный whitespace scan для каждого
  untracked card/change artifact до manifest/staging scope.
- [x] 3.6 Перед review выполнить delivery-manifest working-tree scope-check и
  normalized review preflight; recorded handoff должен описывать review как
  producer GO, не как действие после GO.
