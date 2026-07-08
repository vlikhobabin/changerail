# Drift gate (Фаза 3)

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- OPSX roadmap, раздел 12, Фаза 3 (`docs/opsx-source-of-truth-architecture.md`).
- Раздел 11 (Verification и drift).

## Summary
Реализовать `scripts/smoke-drift.py`, который проходит по configured workspace
roots и показывает, какие проекты подключены к OPSX, какие используют legacy
source, где сломан wiring и какие явно исключены — с machine-readable output для
CI и без публикации machine-local inventory в репозитории.

## Acceptance
- `scripts/smoke-drift.py` проходит по configured workspace roots и
  переиспользует verify-проверки для классификации.
- Есть механизм include/exclude списка проектов; machine-local inventory хранится
  в `internal/`, а не в tracked файлах.
- Machine-readable (JSON) output для CI, красно-зеленый по exit-коду.
- Отчет показывает consumer-классы: OPSX source, legacy source, broken wiring,
  disconnected и explicitly excluded.
- Public safety: в репозиторий не попадают реальные имена проектов и пути.

## Change Set
- `add-workspace-drift-gate`

## Verify
- passed: `python3 -m py_compile scripts/smoke-drift.py`
- expected red: `python3 scripts/smoke-drift.py --config
  .runtime/opsx/drift-smoke/fixture/config.json --run-id fixture-red-final`
  exited non-zero with 2/5 passed and 3 failed drift classes; report
  `.runtime/opsx/drift-smoke/fixture-red-final/report.json`
- passed: `python3 scripts/smoke-drift.py --project
  .runtime/opsx/drift-smoke/fixture/projects/opsx-source --run-id
  fixture-green-final` -> 1/1 passed; report
  `.runtime/opsx/drift-smoke/fixture-green-final/report.json`
- expected red: `python3 scripts/smoke-drift.py --run-id
  no-inventory-final` exited non-zero and reported missing inventory; report
  `.runtime/opsx/drift-smoke/no-inventory-final/report.json`
- passed: `openspec validate add-workspace-drift-gate --strict`
- passed: `openspec validate opsx-drift-gate --strict`
- passed: `openspec validate --all --strict`
- passed: `git diff --check`
- passed: text whitespace scan over modified and untracked files
- passed: targeted public-surface scan over 101 files
- passed: `python3 -m json.tool
  .runtime/opsx/delivery-manifests/03-drift-gate.json`

## Archive
- `openspec/changes/archive/2026-07-08-add-workspace-drift-gate/`

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `docs/wiring-discovery.md`
- `scripts/smoke-wiring-discovery.py`
- `scripts/smoke-drift.py`
- `openspec/changes/archive/2026-07-08-add-workspace-drift-gate/`
- `openspec/specs/opsx-drift-gate/spec.md`

## Result
Implemented and archived `add-workspace-drift-gate`. External review cycle 1
returned a fresh `go` verdict; publish proceeds with ignored runtime artifacts
excluded.

## Next
- Continue with `openspec/board/1.backlog/04-migrate-existing-consumers.md`.

## Change 1: `add-workspace-drift-gate`

### Why
OPSX уже умеет проверять один consumer project через `bin/verify-project`, но
сопровождающему нужен workspace-level red/green smoke, который безопасно
классифицирует configured projects и не публикует machine-local inventory.

### Goal
Добавить `scripts/smoke-drift.py` как CI-friendly drift gate с include/exclude
конфигом, JSON report и consumer-классами: OPSX source, legacy source, broken
wiring, disconnected и explicitly excluded.

### Scope
- `scripts/smoke-drift.py`
- focused smoke/verification fixtures under ignored `.runtime`
- docs/spec updates for the drift report contract and public-safety behavior
- board/card delivery manifest updates for this card

### Acceptance
- Script reads configured workspace roots from an explicit config path or
  CLI/project arguments; no tracked file contains real local project inventory.
- Include/exclude entries classify projects deterministically, with excluded
  projects reported as `explicitly_excluded`.
- Non-excluded projects reuse `bin/verify-project` where applicable and produce
  red/green exit codes.
- JSON report records schema, run id, config source, summary and per-project
  classes without leaking private inventory in tracked files.
- Public examples remain generic (`/opt/opsx`, `/opt/example-project`,
  `/opt/example-a`, `/opt/example-b`).

### Depends On
- `bin/verify-project`
- `openspec/specs/opsx-project-verification/spec.md`

### Related
- `openspec/changes/archive/2026-07-08-add-workspace-drift-gate/`

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 3 remaining scope.
- 2026-07-08T17:05:00Z opsx-ff decomposed the card into
  `add-workspace-drift-gate` and moved it to `2.todo`.
- 2026-07-08T17:10:00Z delivery started; card moved to `3.inprogress`.
- 2026-07-08T17:17:00Z implemented `scripts/smoke-drift.py`, docs and
  `opsx-drift-gate` spec; fixture red/green checks passed as expected.
- 2026-07-08T17:20:00Z archived `add-workspace-drift-gate` after syncing
  specs and validating OpenSpec plus whitespace/public-surface checks.
- 2026-07-08T17:20:00Z safety stop: awaiting external review per supervisor
  instruction; no self-review, reviewer launch, publish, commit or push was
  performed.
- 2026-07-08T17:25:07Z external review cycle 1 returned `go`; verdict
  validated fresh against HEAD `02bb8fc9828707f0d60251c103bb32766692404a`
  with fingerprint
  `sha256:057c0fbdb20ae163adf05dc0f691fe072de75faffd6cbc4faaac0444d1cc34ef`.
- 2026-07-08T17:28:48Z card moved to `4.done` for scoped publish; runtime
  review verdict and delivery manifest remain excluded from commit.
