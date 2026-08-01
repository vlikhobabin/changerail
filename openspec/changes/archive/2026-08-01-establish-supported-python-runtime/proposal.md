## Why

ChangeRail Python helpers сейчас зависят от того, какой host `python3` первым
найден в `PATH`, поэтому consumer projects могут падать поздно: на import
`tomllib`, отсутствии runtime dependency или shebang execution. Единый
supported runtime contract нужен до release hardening, чтобы diagnostics
helper-ов были ранними, воспроизводимыми и actionable.

## What Changes

- Compatibility и migration docs объявляют supported Python version и required
  runtime modules отдельно от release-only tooling.
- Добавляется один shared runtime bootstrap/selection path для ChangeRail
  Python helper entrypoints.
- `verify-project`, delivery manifest, review verdict, delivery runner и
  delivery metrics helpers используют этот shared selection path.
- Поддерживается явный interpreter override без редактирования tracked
  shebangs.
- Bootstrap/runtime environment state записывается только под ignored
  `.runtime/changerail/` paths.
- Добавляется focused smoke coverage для supported runtime selection,
  old-version simulation, missing dependency diagnostics и invalid override.

## Capabilities

### New Capabilities
- `changerail-python-runtime`: supported Python runtime selection, override,
  ignored runtime environment state и actionable diagnostics для ChangeRail
  Python helpers.

### Modified Capabilities
- `changerail-project-verification`: `bin/verify-project` adopts the shared
  Python runtime contract.
- `changerail-contracts`: delivery manifest and review verdict helper
  entrypoints adopt the shared Python runtime contract.
- `changerail-delivery-runner`: `bin/changerail-delivery-runner` adopts the
  shared Python runtime contract.
- `changerail-delivery-observability`: `bin/changerail-delivery-metrics` adopts
  the shared Python runtime contract.
- `changerail-release-ci`: release baseline and focused smoke inventory cover
  runtime selection diagnostics.

## Impact

- Affected entrypoints: `bin/verify-project`, `bin/changerail-review-verdict`,
  `bin/changerail-delivery-runner`, `bin/changerail-delivery-metrics` и
  script-level contract helpers, которые вызываются через runtime launcher.
- Affected docs: `docs/compatibility.md`, `docs/migration-guide.md` и related
  release-facing runtime notes.
- Affected verification: focused runtime smoke и local release baseline.
