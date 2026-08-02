# Добавить native Windows runtime entrypoints

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`040-native-windows-implementation`

## Series Index
`01`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `010-02-establish-supported-python-runtime`

## Summary
Реализовать tracked `.cmd` entrypoints и runtime invocation semantics для
OpenSpec and ChangeRail helper commands on native Windows, preserving existing
POSIX entrypoints.

## Acceptance
- `bin/*.cmd` wrappers exist for supported Windows helper surfaces: OpenSpec,
  `changerail-python`, `verify-project`, `changerail-review-verdict`,
  `changerail-evidence`, delivery runner and metrics.
- `.cmd` wrappers preserve argv, exit code, cwd and environment.
- Paths with spaces and non-ASCII are covered by deterministic tests.
- OpenSpec Windows launch uses the same pinned OpenSpec version contract and
  does not call extensionless POSIX wrapper or implicit Bash.
- Python-backed helpers use the shared Python runtime selector and emit
  actionable diagnostics for missing Python, unsupported Python or missing
  runtime dependency.
- PowerShell remains diagnostic/explicit fallback, not the primary default.
- Existing POSIX entrypoints keep compatibility.

## Depends On
- `030-03-freeze-native-windows-architecture`
- `010-02-establish-supported-python-runtime`

## Change Set
- `openspec/changes/archive/2026-08-02-add-native-windows-command-wrappers/`
- `openspec/changes/archive/2026-08-02-test-native-windows-entrypoints/`

## Verify
- Fast-forward artifact validation:
  `bin/openspec validate add-native-windows-command-wrappers --strict` ->
  passed.
- Fast-forward artifact validation:
  `bin/openspec validate test-native-windows-entrypoints --strict` -> passed.
- Fast-forward artifact validation: `bin/openspec validate --all --strict` ->
  passed, 22 items.
- Fast-forward whitespace checks: `git diff --check` -> passed; `rg -n
  "[ \t]$" openspec/changes/add-native-windows-command-wrappers
  openspec/changes/test-native-windows-entrypoints` -> no trailing whitespace
  findings in new untracked artifacts.
- Wrapper implementation checks: `python3 -m py_compile
  scripts/changerail_python_windows.py` -> passed; explicit wrapper inventory
  check for seven `.cmd` files -> passed; static scan for `bash`, `powershell`,
  `pwsh` and `cmd /c` in `.cmd` wrappers -> no matches.
- Focused deterministic entrypoint smoke:
  `python3 scripts/smoke-windows-entrypoints.py --json` -> passed, 49/49
  checks. Coverage included `.cmd` inventory, Python selector routing, pinned
  OpenSpec launch, argv, cwd, environment, exit code, spaces and non-ASCII
  fixture values, and negative unsupported-launch assumptions.
- Release CI contract smoke: `python3 scripts/smoke-release-ci.py` -> passed,
  41/41 checks.
- Ruff after `.cmd` lint exclusion: `ruff check bin scripts` -> passed.
- Public-surface scan: `python3 scripts/public-surface-scan.py` -> passed,
  707 files scanned, 0 findings.
- Delivery validation before archive:
  `bin/openspec validate test-native-windows-entrypoints --strict` -> passed;
  `bin/openspec validate changerail-windows-runtime-entrypoints --strict` ->
  passed; `bin/openspec validate changerail-release-ci --strict` -> passed;
  `bin/openspec validate --all --strict` -> passed, 22 items.
- Full release baseline: `python3 scripts/run-release-baseline.py` -> passed,
  28/28 steps, including current/history public-surface scans and the new
  Windows entrypoint smoke.
- Post-archive validation: `bin/openspec validate --all --strict` -> passed,
  21 items; `git diff --check` -> passed; `bin/openspec list --json` ->
  `{"changes":[]}`.
- Live Windows host smoke was not run from this Linux workspace. This delivery
  records that as an explicit caveat and does not claim live host coverage;
  later `040` cards own live automated smoke and end-to-end host proof.

## Archive
- `add-native-windows-command-wrappers` ->
  `openspec/changes/archive/2026-08-02-add-native-windows-command-wrappers/`.
- `test-native-windows-entrypoints` ->
  `openspec/changes/archive/2026-08-02-test-native-windows-entrypoints/`.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `bin/openspec`
- `bin/openspec.cmd`
- `bin/changerail-python`
- `bin/changerail-python.cmd`
- `bin/verify-project`
- `bin/verify-project.cmd`
- `bin/changerail-review-verdict`
- `bin/changerail-review-verdict.cmd`
- `bin/changerail-evidence`
- `bin/changerail-evidence.cmd`
- `scripts/changerail_python_windows.py`
- `scripts/smoke-windows-entrypoints.py`
- `openspec/specs/changerail-windows-runtime-entrypoints/spec.md`

## Change 1: `add-native-windows-command-wrappers`

### Why
Native Windows cannot execute extensionless POSIX wrappers as process
entrypoints, so supported helper surfaces need tracked Windows-native command
wrappers.

### Goal
Add `.cmd` wrappers for the supported helper commands while preserving existing
POSIX behavior and the shared Python runtime contract.

### Acceptance
- Supported helper commands have tracked `.cmd` wrappers.
- Wrappers preserve argv, cwd, environment and exit code.
- Missing or unsupported Python diagnostics remain actionable.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-02-add-native-windows-command-wrappers/`

## Change 2: `test-native-windows-entrypoints`

### Why
The command wrappers must be regression-tested for Windows path, quoting and
process-launch behavior before wiring or bootstrap code depends on them.

### Goal
Add deterministic tests for Windows command invocation semantics and Linux/POSIX
regression coverage for existing wrappers.

### Acceptance
- Tests cover argv, cwd, env, exit code, spaces and non-ASCII paths.
- Negative coverage documents extensionless launch and implicit Bash
  assumptions.
- Linux release baseline remains green.

### Depends On
- `add-native-windows-command-wrappers`

### Related
- `openspec/changes/archive/2026-08-02-test-native-windows-entrypoints/`

## Result
Implemented tracked native Windows `.cmd` entrypoints for the supported helper
surface, added the Windows selector backend for Python-backed helpers, wired a
focused deterministic entrypoint smoke into local release baseline and CI, synced
specs, and archived both card-owned OpenSpec changes. Live Windows host smoke is
an explicit caveat for later `040` cards.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z provisional card создана из Win32 wrapper report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: `.cmd` wrappers selected as
  native Windows runtime default.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
- 2026-08-02T08:35:52Z `$changerail-deliver` fast-forward создал OpenSpec
  artifacts для `add-native-windows-command-wrappers` и
  `test-native-windows-entrypoints`, validation green; карточка переведена в
  `3.inprogress`.
- 2026-08-02T08:53:31Z delivery реализовал `.cmd` wrappers, Windows Python
  selector backend и deterministic entrypoint smoke; release baseline passed
  28/28, оба OpenSpec changes archived, карточка оставлена в `3.inprogress`
  для fresh independent review.
- 2026-08-02T09:06:55Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
