# Добавить native Windows wiring backend

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`040-native-windows-implementation`

## Series Index
`02`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `040-01-add-windows-runtime-entrypoints`

## Summary
Реализовать generated project-local Windows wiring backend in bootstrap and
adoption/discovery surfaces, with explicit symlink and junction fallbacks.

## Acceptance
- Bootstrap chooses Windows generated-copy default deterministically by platform
  and project policy.
- Generated command, skill and helper wiring artifacts are owned by a manifest
  or tracked project policy with source identity, digest/refresh semantics and
  project-owned divergence handling.
- Default Windows path does not require Developer Mode, administrator elevation
  or symlink privileges.
- Directory and file wiring are classified separately.
- Symlink fallback requires explicit operator opt-in and positive
  privilege/Developer Mode proof.
- Junction fallback requires explicit operator opt-in, link-aware cleanup and
  Git-safety preconditions.
- Partial failure rolls back only artifacts created by the current run.
- Dry-run reports selected backend, generated ownership and fallback reasons.
- Upgrade/refresh updates only generated-owned files and never silently
  overwrites project-owned files.
- Existing POSIX symlink wiring remains compatible.

## Depends On
- `040-01-add-windows-runtime-entrypoints`
- `030-03-freeze-native-windows-architecture`

## Change Set
- `openspec/changes/archive/2026-08-02-add-windows-generated-wiring-backend/`
- `openspec/changes/archive/2026-08-02-add-windows-wiring-refresh-and-fallbacks/`

## Verify
- Fast-forward artifact validation:
  `openspec validate add-windows-generated-wiring-backend --strict` -> passed.
- Fast-forward artifact validation:
  `openspec validate add-windows-wiring-refresh-and-fallbacks --strict` -> passed.
- Fast-forward artifact validation: `openspec validate --all --strict` ->
  passed, 23 items.
- Fast-forward whitespace checks: `git diff --check` -> passed; `rg -n
  "[ \t]$" openspec/changes/add-windows-generated-wiring-backend
  openspec/changes/add-windows-wiring-refresh-and-fallbacks` -> no trailing
  whitespace findings in new artifacts.
- Syntax check: `python3 -m py_compile bin/bootstrap-project
  bin/verify-project scripts/smoke-bootstrap-project.py
  scripts/smoke-verify-project.py` -> passed.
- Lint: `ruff check bin scripts` -> passed.
- Focused bootstrap smoke before review: `python3 scripts/smoke-bootstrap-project.py`
  -> passed, 11/11 checks. Coverage included POSIX default regression, Windows
  generated-copy dry-run, generated ownership manifest, no-symlink generated
  target and simulated partial failure rollback.
- Focused verifier smoke before review: `python3 scripts/smoke-verify-project.py`
  -> passed, 30/30 checks. Coverage included generated Windows wiring pass,
  stale generated-copy failure, project-owned divergence failure, refresh
  command, and missing proof failures for symlink and junction fallback.
- Public-surface scan: `python3 scripts/public-surface-scan.py` -> passed,
  722 files scanned, 0 findings.
- Delivery validation before archive:
  `openspec validate add-windows-generated-wiring-backend --strict` -> passed;
  `openspec validate add-windows-wiring-refresh-and-fallbacks --strict` ->
  passed; affected capability validations for `changerail-project-bootstrap`,
  `changerail-project-verification`, `changerail-windows-native-architecture`
  and `changerail-wiring-discovery` -> passed; `openspec validate --all
  --strict` -> passed, 23 items.
- Full release baseline: `python3 scripts/run-release-baseline.py` -> passed,
  28/28 steps.
- Independent review cycle 1 returned `no-go` on blockers R1/R2: fallback proof
  was assertion-only, and junction fallback lacked junction-aware
  verification/discovery plus current-run cleanup.
- Same-card rescue replaced assertion-only fallback flags with validated
  `--windows-fallback-proof` reports or native symlink probe, added symlink
  current-run rollback, records symlink/junction-owned artifacts in fallback
  manifests, and adds junction-aware verifier classification.
- Focused bootstrap smoke after rescue: `python3 scripts/smoke-bootstrap-project.py`
  -> passed, 13/13 checks. Added positive symlink fallback proof and symlink
  partial rollback coverage.
- Focused verifier smoke after rescue: `python3 scripts/smoke-verify-project.py`
  -> passed, 32/32 checks. Added verifier acceptance of recorded symlink proof
  and positive junction proof dry-run coverage.
- Post-rescue full release baseline: `python3 scripts/run-release-baseline.py`
  -> passed, 28/28 steps.
- Independent review cycle 2 returned `no-go` on blockers R1/R2: fallback proof
  still accepted status-only assertion reports, and native symlink fallback
  probe wrote under a fresh target before target initialization.
- Same-card rescue cycle 2 now requires schema-valid fallback proof source
  metadata plus concrete per-check evidence, rejects status-only proof reports
  in bootstrap and verifier, and runs the native symlink fallback probe in an
  external temporary directory rather than under the target.
- Focused bootstrap smoke after rescue cycle 2:
  `python3 scripts/smoke-bootstrap-project.py` -> passed, 14/14 checks. Added
  status-only fallback proof rejection coverage.
- Focused verifier smoke after rescue cycle 2:
  `python3 scripts/smoke-verify-project.py` -> passed, 33/33 checks. Added
  status-only fallback manifest rejection coverage.
- Rescue cycle 2 validation: `python3 -m py_compile bin/bootstrap-project
  bin/verify-project scripts/smoke-bootstrap-project.py
  scripts/smoke-verify-project.py` -> passed; `ruff check bin scripts` ->
  passed; `openspec validate --all --strict` -> passed, 21 items; `git diff
  --check` -> passed.
- Post-rescue cycle 2 full release baseline:
  `python3 scripts/run-release-baseline.py` -> passed, 28/28 steps.
- Independent review cycle 3 returned `no-go` on blocker R1: fallback proof
  could still pass with source metadata, details and arbitrary hash-only
  evidence but no command, operation, command argv or retained raw output path.
- Same-card rescue cycle 3 now treats output hashes as supplemental only:
  concrete fallback proof evidence must include a command, operation, command
  argv or retained raw output path. Hash-only proof reports fail closed in both
  bootstrap and verifier.
- Focused bootstrap smoke after rescue cycle 3:
  `python3 scripts/smoke-bootstrap-project.py` -> passed, 15/15 checks. Added
  hash-only fallback proof rejection coverage.
- Focused verifier smoke after rescue cycle 3:
  `python3 scripts/smoke-verify-project.py` -> passed, 34/34 checks. Added
  hash-only fallback manifest rejection coverage.
- Rescue cycle 3 validation: `python3 -m py_compile bin/bootstrap-project
  bin/verify-project scripts/smoke-bootstrap-project.py
  scripts/smoke-verify-project.py` -> passed; `ruff check bin scripts` ->
  passed; `openspec validate --all --strict` -> passed, 21 items; `git diff
  --check` -> passed.
- Post-rescue cycle 3 full release baseline:
  `python3 scripts/run-release-baseline.py` -> passed, 28/28 steps.
- Post-archive validation: `openspec validate --all --strict` -> passed,
  21 items; `git diff --check` -> passed; `openspec list --json` ->
  `{"changes":[]}`.
- Live Windows host smoke was not run from this Linux workspace. This delivery
  records that as an explicit caveat and does not claim live host coverage;
  later `040` cards own automated smoke and end-to-end host proof.

## Archive
- `add-windows-generated-wiring-backend` ->
  `openspec/changes/archive/2026-08-02-add-windows-generated-wiring-backend/`.
- `add-windows-wiring-refresh-and-fallbacks` ->
  `openspec/changes/archive/2026-08-02-add-windows-wiring-refresh-and-fallbacks/`.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/4.done/040-01-add-windows-runtime-entrypoints.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `bin/bootstrap-project`
- `bin/verify-project`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`

## Change 1: `add-windows-generated-wiring-backend`

### Why
Windows needs a default wiring backend that works without Developer Mode,
administrator elevation or symlink privileges.

### Goal
Teach bootstrap/adoption surfaces to select generated project-local copies as
the native Windows default and record generated ownership deterministically.

### Acceptance
- Platform and project policy select the generated-copy backend on Windows.
- Generated artifacts include source identity, digest and refresh semantics.
- Dry-run reports backend choice and fallback reasons.

### Depends On
- `040-01-add-windows-runtime-entrypoints`

### Related
- `openspec/changes/archive/2026-08-02-add-windows-generated-wiring-backend/`

## Change 2: `add-windows-wiring-refresh-and-fallbacks`

### Why
Generated copies need safe refresh, rollback and bounded fallback semantics, and
link modes must stay explicit and fail-closed.

### Goal
Add refresh/upgrade, partial rollback, symlink opt-in and junction opt-in logic
that uses the same ownership classification as bootstrap.

### Acceptance
- Refresh updates only generated-owned artifacts.
- Partial failure cleanup removes only files created by the current run.
- Symlink and junction fallback require explicit opt-in and positive evidence.

### Depends On
- `add-windows-generated-wiring-backend`

### Related
- `openspec/changes/archive/2026-08-02-add-windows-wiring-refresh-and-fallbacks/`

## Result
Implemented generated-copy Windows wiring backend for bootstrap, generated
ownership manifest and dry-run reporting; added verifier support for generated
freshness, stale copies, project-owned divergence and explicit Windows fallback
proofs; added generated refresh and current-run rollback behavior; synced specs
and archived both card-owned OpenSpec changes. Existing POSIX symlink wiring
remains the default outside native Windows. Live Windows host smoke remains an
explicit caveat for later `040` cards.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z provisional card создана из symlink privilege report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: generated-copy wiring is
  the native Windows default; symlink/junction are explicit bounded fallbacks.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
- 2026-08-02T09:14:13Z `$changerail-deliver` fast-forward создал OpenSpec
  artifacts для `add-windows-generated-wiring-backend` и
  `add-windows-wiring-refresh-and-fallbacks`, validation green; карточка
  переведена в `3.inprogress`.
- 2026-08-02T09:36:48Z delivery implemented generated-copy Windows wiring,
  refresh, rollback and fallback proof gates; focused smokes and release
  baseline passed; оба OpenSpec changes archived, карточка оставлена в
  `3.inprogress` для fresh independent review.
- 2026-08-02T09:43:44Z independent review cycle 1 returned `no-go` for
  fallback proof and junction fallback blockers; same-card rescue started.
- 2026-08-02T09:51:28Z same-card rescue replaced assertion-only fallback proof
  with validated proof reports/native symlink probe and added fallback rollback
  coverage; fresh re-review required.
- 2026-08-02T10:06:26Z post-rescue full release baseline passed 28/28; fresh
  independent review cycle 2 queued.
- 2026-08-02T10:35:26Z independent review cycle 2 returned `no-go` for
  status-only fallback proof and native symlink probe target pollution; rescue
  cycle 2 tightened fallback proof evidence validation, moved native probing
  outside the target and added regression coverage; fresh re-review required.
- 2026-08-02T10:41:25Z post-rescue cycle 2 full release baseline passed 28/28;
  fresh independent review cycle 3 queued.
- 2026-08-02T10:59:59Z independent review cycle 3 returned `no-go` for
  hash-only fallback evidence; rescue cycle 3 removed hashes from the concrete
  evidence predicate and added bootstrap/verifier regression coverage; fresh
  re-review required.
- 2026-08-02T11:05:53Z post-rescue cycle 3 full release baseline passed 28/28;
  fresh independent review cycle 4 queued.
- 2026-08-02T11:21:48Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
