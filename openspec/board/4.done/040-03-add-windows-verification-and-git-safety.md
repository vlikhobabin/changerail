# Добавить Windows verification, drift и Git safety

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`040-native-windows-implementation`

## Series Index
`03`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

## Summary
Teach `verify-project`, drift checks and Git safety gates to enforce the
Windows generated-copy ownership model and fail closed for unsafe link fallback
or staging behavior.

## Acceptance
- `verify-project` validates Windows generated wiring manifest/policy and
  distinguishes valid generated content, stale copies, missing generated files,
  project-owned divergence and ordinary directories.
- Drift gate detects ChangeRail source updates and reports required refresh for
  generated Windows wiring.
- Git safety checks prove generated, symlink and junction paths do not stage
  ChangeRail source, ignored runtime state, credentials or out-of-scope files.
- Git safety uses porcelain status, `git add --dry-run` and index inspection.
- Symlink and junction fallback verification fails closed when required
  privilege, Developer Mode, cleanup or Git evidence is missing.
- Ignore rules stay minimal and do not hide project-owned source.
- Rename/update/uninstall and partial cleanup scenarios have negative tests.
- Diagnostics do not print credentials, private hostnames or private Windows
  paths.

## Depends On
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

## Change Set
- `openspec/changes/archive/2026-08-02-enforce-windows-wiring-verification/`
- `openspec/changes/archive/2026-08-02-add-windows-git-safety-gates/`

## Verify
- `python3 scripts/smoke-verify-project.py` passed: generated valid/stale,
  missing and project-owned divergence fixtures plus drift classification.
- `python3 scripts/smoke-windows-wiring-git-safety.py` passed `6/6` after
  review rescue: generated, symlink and junction Git status/dry-run/index
  fixtures; incomplete command-only junction proof rejection; scrubbed unsafe
  proof diagnostics; explicit rename/uninstall ownership boundaries.
- `python3 scripts/smoke-bootstrap-project.py` passed after fallback proof
  validator hardening.
- `python3 scripts/smoke-release-ci.py` passed with Windows wiring Git safety
  smoke in required CI inventory.
- `bin/openspec validate <change> --strict`, capability validation,
  `openspec validate --all --strict`, `git diff --check`, untracked artifact
  whitespace scan and `python3 scripts/public-surface-scan.py` passed.
- Live two-host Windows drift/smoke remains for downstream cards `040-04` and
  `040-05`; this card added deterministic local fail-closed fixtures.

## Archive
- `openspec/changes/archive/2026-08-02-enforce-windows-wiring-verification/`
- `openspec/changes/archive/2026-08-02-add-windows-git-safety-gates/`

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/2.todo/040-02-add-windows-wiring-backend.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `bin/verify-project`
- `scripts/smoke-drift.py`
- `scripts/smoke-windows-wiring-git-safety.py`

## Change 1: `enforce-windows-wiring-verification`

### Why
`verify-project` and drift checks need to distinguish generated Windows wiring
from stale, missing or project-owned content.

### Goal
Validate the generated wiring ownership model in project verification and drift
diagnostics.

### Acceptance
- Verifier covers valid, stale, missing and diverged generated artifacts.
- Drift gate reports required refresh after ChangeRail source updates.
- Diagnostics remain sanitized and actionable.

### Depends On
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

### Related
- `openspec/changes/archive/2026-08-02-enforce-windows-wiring-verification/`

## Change 2: `add-windows-git-safety-gates`

### Why
Generated, symlink and junction paths can accidentally expose ChangeRail source,
runtime state or credentials unless Git behavior is verified fail-closed.

### Goal
Add Git status, dry-run add and index checks for Windows wiring modes and
cleanup/rename scenarios.

### Acceptance
- Git safety covers generated, symlink and junction paths.
- Unsafe fallback evidence fails closed.
- Ignore rules remain minimal and do not hide project-owned source.

### Depends On
- `enforce-windows-wiring-verification`

### Related
- `openspec/changes/archive/2026-08-02-add-windows-git-safety-gates/`

## Result
Implementation delivered, specs synced and card-owned changes archived. Review
cycle 1 returned `no-go`; scoped rescue fixed R1-R3 and review cycle 2
returned `go`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and
published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z provisional card создана из Git junction report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: verifier/drift/Git safety
  must enforce generated ownership and explicit link fallback gates.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
- 2026-08-02T11:31:10Z internal `ff` создал apply-ready artifacts для
  `enforce-windows-wiring-verification` и `add-windows-git-safety-gates`;
  `openspec validate <change> --strict` и whitespace checks прошли.
- 2026-08-02T11:48:01Z `do` реализовал verifier/drift/Git safety gates,
  синхронизировал specs и архивировал оба card-owned changes; deterministic
  smoke, OpenSpec validation, whitespace и public-surface scan прошли.
- 2026-08-02T12:08:12Z review rescue fixed R1-R3: Git proof checks now require
  explicit `safe: true` and `unsafe_paths: []`, unsafe proof diagnostics are
  scrubbed, and `scripts/smoke-windows-wiring-git-safety.py` covers incomplete
  proof plus explicit rename/uninstall boundaries; focused and baseline smokes
  passed.
- 2026-08-02T12:19:03Z publish finalized card into `4.done`; exact ledger
  retained in ignored manifest.
