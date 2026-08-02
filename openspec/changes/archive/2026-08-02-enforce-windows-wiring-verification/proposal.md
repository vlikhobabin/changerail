## Why

Windows generated wiring уже имеет manifest, refresh path и fallback proof
model, но verifier и drift coverage должны доказывать fail-closed behavior для
stale, missing и project-owned artifacts. Без этих negative gates consumer
может выглядеть ChangeRail-wired, хотя содержит stale generated copies или
небезопасные fallback metadata.

## What Changes

- Ужесточить `verify-project` checks для generated Windows wiring: fresh,
  stale, missing и project-owned generated artifacts.
- Расширить drift classification, чтобы generated Windows consumers со stale
  или diverged wiring не классифицировались как current ChangeRail source.
- Сохранять refresh diagnostics actionable, но не печатать private paths,
  hostnames, credential contents или raw Windows lab output.
- Добавить deterministic smoke fixtures для valid generated wiring, stale
  source updates, missing generated files, project-owned divergence и refresh.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-verification`: generated Windows wiring ownership,
  freshness, missing-artifact и divergence checks.
- `changerail-drift-gate`: generated Windows wiring drift classification и
  refresh remediation reporting.
- `changerail-wiring-discovery`: generated Windows wiring freshness diagnostics,
  которые потребляют verification и drift gates.
- `changerail-windows-native-architecture`: concrete generated verification и
  drift behavior для selected Windows default.

## Impact

- `bin/verify-project`.
- `scripts/smoke-verify-project.py`.
- `scripts/smoke-drift.py`.
- `scripts/run-release-baseline.py` и CI smoke coverage, если добавляются новые
  focused checks.
- `docs/wiring-discovery.md`.
- OpenSpec specs для project verification, drift, wiring discovery и Windows
  native architecture.
