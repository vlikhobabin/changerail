## Why

После live clean-clone proof ChangeRail должен обновить публичные compatibility
и migration docs так, чтобы native Windows support claim соответствовал
реально сохраненной sanitized evidence. Документы не должны продолжать
описывать Windows support как future/planned или скрывать residual caveats.

## What Changes

- Обновить compatibility matrix по результатам two-host clean-clone proof,
  Windows smoke matrix и Linux release baseline.
- Добавить migration/adoption guidance для native Windows operators:
  `.cmd` helper usage, generated-copy default wiring, refresh, verification и
  blocker/caveat handling.
- Зафиксировать public-safe evidence paths и verification outcomes без raw
  hostnames, SSH targets, credentials или machine-local Windows paths.
- Обновить release-facing docs так, чтобы full support claim зависел от
  Windows live proof, current/history public-surface scans и Linux baseline.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-windows-support-matrix`: tracked matrix records final support
  claim evidence, caveats and retained ignored report paths.
- `changerail-release-discipline`: release/support docs require the final
  Windows proof, public-surface scans and release baseline before claiming
  support.

## Impact

- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/consumer-adoption-runbook.md`
- `docs/release-discipline.md`
- Windows support matrix and release discipline specs
- card verification/result/archive notes
