## Why

Серия `030-native-windows-discovery` получила two-host evidence по Windows
runtime, wiring и Git behavior. Перед началом серии `040` нужен один
evidence-backed default path с ограниченными fallback-ами, чтобы реализация не
опиралась на несовместимые предположения о Bash, symlink privileges, junction
traversal или extensionless wrappers.

## What Changes

- Зафиксировать native Windows architecture decision для runtime entrypoints,
  project wiring, tracked/generated ownership, drift/upgrade и cleanup.
- Описать prerequisites для supported Windows path: shell, Python, Git,
  Developer Mode/elevation policy и operator-managed lab assumptions.
- Добавить threat model для junction traversal, accidental staging,
  credentials, command quoting и untrusted repository content.
- Зафиксировать mandatory Windows test matrix для implementation серии `040`.
- Обновить compatibility notes и board handoff без реализации runtime code.

## Capabilities

### New Capabilities
- `changerail-windows-native-architecture`: durable support contract for the
  selected native Windows runtime, wiring, fallback, threat and test model.

### Modified Capabilities
- none

## Impact

- Updates `docs/compatibility.md` with the final `030-03` architecture decision.
- Adds a main OpenSpec capability for future Windows implementation work.
- Updates the `030-03` board card with ordered changes and verification handoff.
- Does not change `bin/bootstrap-project`, `bin/verify-project`, templates,
  shims, scripts or runtime behavior.
