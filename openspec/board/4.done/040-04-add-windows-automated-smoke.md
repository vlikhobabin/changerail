# Добавить automated native Windows smoke matrix

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`040-native-windows-implementation`

## Series Index
`04`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

## Summary
Превратить research probes в deterministic Windows regression suite for `.cmd`
entrypoints, generated wiring, verifier/drift, Git safety, cleanup and
fallback behavior.

## Acceptance
- Test suite runs non-interactively on supported native Windows environments.
- Deterministic local fixtures cover `.cmd` launch, generated copy ownership,
  stale copy detection, explicit refresh, project-owned divergence, cleanup,
  Git status/add/index behavior, spaces and non-ASCII paths.
- Live matrix covers both `windows-host-a` and `windows-host-b`, or records an
  explicit blocker/caveat before claiming host coverage.
- Matrix covers generated-copy default and bounded symlink/junction fallback
  negative/positive conditions.
- Tests use disposable workspaces and idempotent cleanup.
- Host-specific failures create sanitized structured report under ignored
  runtime state.
- Linux release baseline includes platform-neutral contract tests.
- Local two-host run and future Windows CI integration path are documented.

## Depends On
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

## Change Set
- `openspec/changes/archive/2026-08-02-add-windows-smoke-matrix-runner/`
- `openspec/changes/archive/2026-08-02-document-windows-smoke-operations/`

## Verify
- Fast-forward artifact validation:
  `openspec validate add-windows-smoke-matrix-runner --strict` -> passed.
- Fast-forward artifact validation:
  `openspec validate document-windows-smoke-operations --strict` -> passed.
- Fast-forward artifact validation: `openspec validate --all --strict` ->
  passed, 23 items.
- Fast-forward whitespace checks: `git diff --check` -> passed; `rg -n
  "[ \t]$" openspec/changes/add-windows-smoke-matrix-runner
  openspec/changes/document-windows-smoke-operations` -> no trailing
  whitespace findings in new artifacts.
- Release CI RED check before workflow wiring:
  `python3 scripts/smoke-release-ci.py` -> failed as expected with missing
  `python3 scripts/smoke-windows-matrix.py` command.
- Runner syntax and lint: `python3 -m py_compile
  scripts/smoke-windows-matrix.py` -> passed; `ruff check bin scripts` ->
  passed.
- Matrix local smoke: `python3 scripts/smoke-windows-matrix.py --json` ->
  passed, 6/7 items passed and live host coverage explicitly `not-run`.
- Matrix repeat smoke: `python3 scripts/smoke-windows-matrix.py --repeat
  --json` -> passed, 12/14 local items passed, 0 repeat mismatches, live host
  coverage explicitly `not-run`.
- Matrix live smoke: `python3 scripts/smoke-windows-matrix.py --live --json`
  -> passed, 8/8 items passed; `windows-host-a` and `windows-host-b` passed
  lab readiness and runtime/wiring live smoke through ignored inventory.
- Live matrix retained report:
  `.runtime/changerail/windows-smoke/20260802T124109Z-9b50bc37/report.json`
  (ignored runtime evidence; raw child output retained only under that ignored
  run directory).
- Documentation/config checks: `python3 -m json.tool .mcp.json` -> passed;
  TOML parse for `.codex/config.toml` -> `TOML_OK`.
- Public-surface scan: `python3 scripts/public-surface-scan.py` -> passed,
  752 files scanned, 0 findings.
- Post-archive validation: `openspec validate --all --strict` -> passed,
  22 items; `git diff --check` -> passed; `openspec list --json` ->
  `{"changes":[]}`.
- Full release baseline: `python3 scripts/run-release-baseline.py` -> passed,
  30/30 steps, including platform-neutral Windows smoke matrix, current/history
  public-surface scans, OpenSpec validation, ruff, focused smokes and drift
  fixture.

## Archive
- `add-windows-smoke-matrix-runner` ->
  `openspec/changes/archive/2026-08-02-add-windows-smoke-matrix-runner/`.
- `document-windows-smoke-operations` ->
  `openspec/changes/archive/2026-08-02-document-windows-smoke-operations/`.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/2.todo/040-03-add-windows-verification-and-git-safety.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`
- `scripts/smoke-windows-matrix.py`
- `scripts/smoke-windows-entrypoints.py`
- `scripts/smoke-windows-wiring-git-safety.py`
- `docs/compatibility.md`
- `docs/release-discipline.md`
- `docs/wiring-discovery.md`
- `openspec/specs/changerail-windows-smoke-matrix/spec.md`

## Change 1: `add-windows-smoke-matrix-runner`

### Why
Research probes must become deterministic regression coverage that can be
rerun non-interactively on native Windows hosts.

### Goal
Add a Windows smoke matrix runner for entrypoints, generated wiring,
verification, drift, Git safety, cleanup and fallback behavior.

### Acceptance
- Matrix runs non-interactively against `windows-host-a` and `windows-host-b`.
- Reports are sanitized and retained only under ignored runtime state.
- Fixtures use disposable workspaces and idempotent cleanup.

### Depends On
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

### Related
- `openspec/changes/archive/2026-08-02-add-windows-smoke-matrix-runner/`

## Change 2: `document-windows-smoke-operations`

### Why
Operators need a repeatable local two-host workflow and a clear future CI path
without exposing private SSH details.

### Goal
Document how to run, interpret and retain Windows smoke evidence, including
explicit blocker/caveat handling.

### Acceptance
- Docs describe local two-host execution and sanitized evidence retention.
- Future Windows CI integration path is documented.
- Linux release baseline includes platform-neutral contract tests.

### Depends On
- `add-windows-smoke-matrix-runner`

### Related
- `openspec/changes/archive/2026-08-02-document-windows-smoke-operations/`

## Result
Implemented aggregate Windows smoke matrix runner, wired the platform-neutral
matrix into release baseline and CI inventory, documented local/repeat/live
operator workflow and future Windows CI boundary, synced specs and archived
both card-owned OpenSpec changes. Live two-host smoke passed through ignored
inventory and retained sanitized evidence under ignored runtime state.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z provisional test card создана для обязательной Windows matrix.
- 2026-08-02T07:27:00Z refreshed against `030-03`: smoke must cover `.cmd`,
  generated-copy default, explicit fallbacks, cleanup and Git safety.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
- 2026-08-02T12:26:05Z internal `ff` создал apply-ready artifacts для
  `add-windows-smoke-matrix-runner` и
  `document-windows-smoke-operations`; OpenSpec validation and whitespace
  checks passed; карточка переведена в `3.inprogress`.
- 2026-08-02T12:56:05Z `do` реализовал aggregate Windows smoke matrix,
  проверил local/repeat/live matrix, синхронизировал specs, архивировал оба
  card-owned changes и оставил карточку в `3.inprogress` для fresh independent
  review.
- 2026-08-02T13:07:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
