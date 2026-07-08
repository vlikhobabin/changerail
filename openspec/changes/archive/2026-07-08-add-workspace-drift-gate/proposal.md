## Why

`bin/verify-project` проверяет один consumer project, но сопровождающему нужен
workspace-level drift gate: какие проекты уже подключены к OPSX, какие еще
смотрят на legacy source, где wiring сломан и какие проекты явно исключены.
Этот отчет должен быть machine-readable для CI и не должен превращать
machine-local inventory в tracked public surface.

## What Changes

- Добавить `scripts/smoke-drift.py` как красно-зеленый smoke/gate для
  configured workspace roots и явного списка projects.
- Добавить JSON contract для drift report с consumer classes:
  `opsx_source`, `legacy_source`, `broken_wiring`, `disconnected`,
  `explicitly_excluded`.
- Реиспользовать `bin/verify-project` для non-excluded OPSX-like projects,
  когда project содержит project-local `bin/verify-project` или OPSX wrapper
  `bin/openspec`/agent wiring.
- Поддержать include/exclude config, который хранится в operator-specified
  path such as `internal/`, а не в tracked files.
- Добавить focused smoke coverage с generic runtime fixtures under `.runtime`.

## Capabilities

### New Capabilities
- `opsx-drift-gate`: workspace-level drift report/gate for OPSX consumer
  projects, legacy consumers, broken wiring, disconnected projects and explicit
  exclusions.

### Modified Capabilities
- none

## Impact

- Adds `scripts/smoke-drift.py`.
- Adds `openspec/specs/opsx-drift-gate/spec.md` after sync.
- May update README/architecture docs to reference the implemented drift gate.
- Runtime reports and machine-local inventory remain ignored under `.runtime`
  or operator-owned `internal/`.
