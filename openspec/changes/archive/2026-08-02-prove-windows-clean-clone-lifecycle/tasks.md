## 1. Native Entrypoint Surface

- [x] 1.1 Add `bin/bootstrap-project.cmd` and include it in deterministic
  Windows entrypoint smoke coverage.
- [x] 1.2 Update runtime entrypoint docs/spec references so bootstrap is part
  of the native Windows helper surface.

## 2. Clean-Clone Lifecycle Harness

- [x] 2.1 Add `scripts/windows-clean-clone-lifecycle.py` with sample dry-run
  and live SSH modes using ignored Windows lab inventory.
- [x] 2.2 In live mode, clone the requested ChangeRail ref on each host,
  launch native `.cmd` helpers, bootstrap a generated-copy consumer, run
  `verify-project.cmd`, check discovery, refresh generated wiring and prove
  explicit no-push staging excludes ignored runtime files.
- [x] 2.3 Sanitize reports and retain raw command output only under ignored
  `.runtime/changerail/` evidence paths.

## 3. Matrix Integration

- [x] 3.1 Add clean-clone lifecycle proof to
  `scripts/smoke-windows-matrix.py --live`.
- [x] 3.2 Ensure local/default matrix still runs without contacting Windows
  hosts and records live coverage as not-run unless requested.

## 4. Verification

- [x] 4.1 Run `python3 -m py_compile scripts/windows-clean-clone-lifecycle.py
  scripts/smoke-windows-matrix.py scripts/smoke-windows-entrypoints.py`.
- [x] 4.2 Run `python3 scripts/smoke-windows-entrypoints.py --json`.
- [x] 4.3 Run `python3 scripts/windows-clean-clone-lifecycle.py dry-run
  --sample --json`.
- [x] 4.4 Run `python3 scripts/smoke-windows-matrix.py --json`.
- [x] 4.5 Run `python3 scripts/smoke-windows-matrix.py --live --inventory
  internal/windows-lab-inventory.json --json` and retain the sanitized report,
  or record an explicit support blocker.
- [x] 4.6 Run `openspec validate prove-windows-clean-clone-lifecycle --strict`
  and `git diff --check`.
