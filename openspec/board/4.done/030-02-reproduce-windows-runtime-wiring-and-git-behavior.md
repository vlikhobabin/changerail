# Воспроизвести Windows runtime, wiring и Git behavior

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`030-native-windows-discovery`

## Series Index
`02`

## Source
- Consolidated native Windows reports от 2026-08-01.

## Summary
На обоих Windows hosts воспроизвести три исходных дефекта и сравнить candidate
strategies для directory/file wiring, wrapper invocation, Git staging, drift и
upgrade behavior.

## Acceptance
- Проверен direct `os.symlink` без elevation и с доступным Developer Mode.
- Проверены junction behavior и `git status`/`git add --dry-run` traversal.
- Проверен direct subprocess launch extensionless `bin/openspec` и варианты
  `.cmd`, PowerShell, Python и explicit bash invocation.
- Проверены file links отдельно от directory links.
- Для generated copy измерены drift detection и source update behavior.
- Каждый probe выполнен на `windows-host-a` и `windows-host-b` либо имеет
  explicit not-applicable reason.
- Создана sanitized comparison table с security, portability, Git и operator
  trade-offs.

## Scope
- Disposable consumer fixture и remote probe runner.
- Evidence, достаточное для architecture decision.

## Non-Goals
- Выбор architecture до получения результатов.
- Изменение реальных consumer worktrees.

## Depends On
- `030-01-establish-windows-lab-and-support-matrix`

## Implementation Notes
- Использовать `git ls-files`, porcelain status и index inspection, а не только
  console display.
- Проверять checkout/clone повторно: generated local wiring и tracked wiring
  имеют разные lifecycle semantics.

## Change Set
- `add-windows-runtime-wiring-probe`
- `capture-windows-runtime-wiring-results`

## Archive
- `add-windows-runtime-wiring-probe` ->
  `openspec/changes/archive/2026-08-02-add-windows-runtime-wiring-probe/`.
- `capture-windows-runtime-wiring-results` ->
  `openspec/changes/archive/2026-08-02-capture-windows-runtime-wiring-results/`.

## Verify
- `python3 scripts/windows-runtime-wiring-probe.py dry-run --sample --json` ->
  passed; sample report shape includes both generic host ids and 28 sample
  checks.
- `python3 -m py_compile scripts/windows-runtime-wiring-probe.py` -> passed.
- `python3 scripts/windows-runtime-wiring-probe.py run --inventory internal/windows-lab-inventory.json --json` ->
  passed; retained sanitized primary report at
  `.runtime/changerail/windows-runtime-wiring/20260802T070216Z/report.json`.
- Repeatability run after cleanup:
  `python3 scripts/windows-runtime-wiring-probe.py run --inventory internal/windows-lab-inventory.json --json` ->
  passed; retained sanitized repeatability report at
  `.runtime/changerail/windows-runtime-wiring/20260802T070225Z/report.json`;
  0 per-check status mismatches versus primary.
- `python3 scripts/public-surface-scan.py` -> passed, 673 files scanned,
  0 findings.
- `./bin/openspec validate add-windows-runtime-wiring-probe --strict` -> passed.
- `./bin/openspec validate capture-windows-runtime-wiring-results --strict` -> passed.
- `./bin/openspec validate --all --strict` -> passed, 18 items passed.
- `git diff --check` -> passed.
- RED evidence: not applicable; this card adds a research harness and publishes
  observed lab evidence rather than changing a production runtime behavior.

## Change 1: `add-windows-runtime-wiring-probe`

### Why
Нужно воспроизводимо проверить исходные Windows runtime, wiring и Git
поведения без изменения реальных consumer worktrees и без записи private host
identity в tracked files.

### Goal
Добавить public-safe harness для disposable two-host Windows probes: symlink,
junction, file link, wrapper launch, Git traversal, generated-copy drift и
cleanup semantics.

### Scope
- Stdlib Python harness that reuses ignored Windows lab inventory.
- Remote Python probe script executed non-interactively inside disposable roots.
- Sanitized JSON report and dry-run validation shape.

### Acceptance
- Harness checks direct `os.symlink`, junction behavior, file links, wrapper
  invocation variants, Git status/add traversal, generated copy drift and source
  update semantics.
- Raw host output remains under ignored `.runtime/changerail/`.
- Dry-run sample validates the public report shape without contacting hosts.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-02-add-windows-runtime-wiring-probe/`

## Change 2: `capture-windows-runtime-wiring-results`

### Why
Architecture work in `030-03` needs observed two-host trade-offs, not assumed
Windows behavior.

### Goal
Run the probe on `windows-host-a` and `windows-host-b`, retain ignored evidence,
and publish a sanitized comparison table with security, portability, Git and
operator trade-offs.

### Scope
- Live probe execution against both ignored inventory hosts.
- Sanitized compatibility notes and card verification summary.
- Public-surface scan covering tracked results.

### Acceptance
- Each host has a result or explicit not-applicable reason for each card
  acceptance criterion.
- Comparison table distinguishes directory links, file links, wrapper launch
  variants and generated-copy lifecycle behavior.
- Repeatability run after cleanup produces the same strategy conclusions.

### Depends On
- `add-windows-runtime-wiring-probe`

### Related
- `openspec/changes/archive/2026-08-02-capture-windows-runtime-wiring-results/`

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `docs/compatibility.md`
- `bin/bootstrap-project`
- `bin/verify-project`
- `scripts/windows-runtime-wiring-probe.py`
- `scripts/smoke-wiring-discovery.py`
- `openspec/changes/archive/2026-08-02-add-windows-runtime-wiring-probe/`
- `openspec/changes/archive/2026-08-02-capture-windows-runtime-wiring-results/`

## Result
Implementation verified. Primary and repeatability probes passed on both hosts;
sanitized comparison table recorded in `docs/compatibility.md`.

Observed architecture inputs for `030-03`:
- direct extensionless `bin/openspec` subprocess launch failed on both hosts
  with Win32 application error;
- `.cmd`, PowerShell and Python wrapper variants passed on both hosts;
- explicit Bash was unsupported on `windows-host-a` and failed through the
  host Bash/WSL environment on `windows-host-b`;
- direct directory and file `os.symlink` passed under current SSH tokens, but
  non-elevated Developer Mode behavior is not applicable because both tokens
  reported `elevated=true` and Developer Mode stayed `unknown`;
- junction behavior passed on both hosts;
- generated copy drift was observable after source update, and explicit refresh
  picked up the source update on both hosts;
- `git status --porcelain`, `git add --dry-run` and `git ls-files --stage`
  observed all linked/generated paths on both hosts.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z три исходных Windows reports объединены в один research scope.
- 2026-08-02T05:48:42Z переведена в `2.todo` после readiness pass: оба
  Windows hosts доступны через ignored inventory, story зависит от lab protocol
  и support matrix из `030-01`.
- 2026-08-02T06:39:56Z `$changerail-deliver` начал fast-forward planning:
  добавлены ordered changes `add-windows-runtime-wiring-probe` и
  `capture-windows-runtime-wiring-results`.
- 2026-08-02T06:39:56Z fast-forward завершен: OpenSpec artifacts для обоих
  changes созданы и прошли validation; карточка переведена в `3.inprogress`.
- 2026-08-02T07:04:37Z live Windows runtime/wiring probe и repeatability rerun
  прошли на `windows-host-a` и `windows-host-b`; tracked comparison table
  обновлена только sanitized generic host ids и ignored evidence paths.
- 2026-08-02T07:04:37Z delivery завершил sync/archive для
  `add-windows-runtime-wiring-probe` и
  `capture-windows-runtime-wiring-results`; карточка оставлена в
  `3.inprogress` до fresh independent review.
- 2026-08-02T07:09:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
