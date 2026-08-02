# Подготовить Windows lab и support matrix

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`030-native-windows-discovery`

## Series Index
`01`

## Source
- Доступны два operator-managed native Windows laptop для SSH исследований.

## Summary
Определить безопасный remote research protocol, собрать sanitized capability
matrix двух hosts и подготовить disposable workspaces для воспроизводимых
Windows probes.

## Acceptance
- Для каждого host зафиксированы sanitized OS/filesystem/Git/Python/shell и
  privilege capabilities.
- Проверены SSH access, non-interactive command execution и безопасная передача
  test fixtures без записи credentials в repository.
- Созданы disposable test roots вне реальных consumer repositories.
- Определены cleanup, timeout и evidence retention rules.
- Tracked report использует generic `windows-host-a`/`windows-host-b`; mapping и
  raw connection data остаются ignored.
- Lab protocol запрещает elevation без отдельного operator action.

## Scope
- Research harness/protocol и compatibility matrix.
- Ignored operator inventory schema/notes при необходимости.

## Non-Goals
- Изменение ChangeRail runtime или bootstrap behavior.
- Постоянная CI infrastructure registration.

## Depends On
- Серия `010-core-release-contracts` завершена.

## Implementation Notes
- Команды должны быть idempotent и ограничены disposable workspace.
- Retained public evidence содержит command class и outcome, но не host identity.

## Change Set
- `establish-windows-lab-protocol`
- `capture-windows-support-matrix`

## Verify
- `python3 scripts/windows-lab-probe.py dry-run --sample --json` -> passed;
  validates generic inventory/report shape without contacting real hosts.
- `python3 scripts/windows-lab-probe.py dry-run --inventory internal/windows-lab-inventory.json --json` -> passed;
  ignored two-host inventory has required generic ids and is Git-ignored.
- `python3 scripts/windows-lab-probe.py run --inventory internal/windows-lab-inventory.json --json` -> passed;
  retained sanitized report at
  `.runtime/changerail/windows-lab/20260802T060958Z/report.json`; both hosts
  passed SSH access, non-interactive PowerShell execution, disposable root
  setup, fixture transfer and cleanup.
- `python3 -m py_compile scripts/windows-lab-probe.py` -> passed.
- `python3 scripts/public-surface-scan.py` -> passed, 660 files scanned,
  0 findings.
- `./bin/openspec validate establish-windows-lab-protocol --strict` -> passed.
- `./bin/openspec validate capture-windows-support-matrix --strict` -> passed.
- `./bin/openspec validate --all --strict` -> passed.
- `git diff --check` -> passed.
- RED evidence: not applicable; this card adds research protocol/docs and a
  live lab harness, verified through dry-run, live non-destructive probes and
  public-surface scan rather than a regression unit test.

## Archive
- `establish-windows-lab-protocol` ->
  `openspec/changes/archive/2026-08-02-establish-windows-lab-protocol/`.
- `capture-windows-support-matrix` ->
  `openspec/changes/archive/2026-08-02-capture-windows-support-matrix/`.

## Change 1: `establish-windows-lab-protocol`

### Why
Серия `030` должна выполнять native Windows probes через operator-managed SSH
без записи identities, credentials или raw session data в публичный tracked
surface.

### Goal
Зафиксировать reusable lab protocol, ignored inventory contract, timeout,
cleanup, evidence retention и no-elevation правила для disposable Windows
research workspaces.

### Scope
- Tracked protocol/harness documentation for native Windows research.
- Local dry-run harness validation that does not require Windows hosts.
- Public-safe OpenSpec requirements for the lab protocol.

### Acceptance
- Protocol names only `windows-host-a` and `windows-host-b` in tracked output.
- Disposable roots are outside consumer repositories and cleanup is idempotent.
- Commands run non-interactively with bounded timeout and no elevation.
- Raw host mapping and connection command data remain ignored.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-02-establish-windows-lab-protocol/`

## Change 2: `capture-windows-support-matrix`

### Why
Before reproducing Windows wiring failures, ChangeRail needs a sanitized
capability matrix proving both hosts can run controlled probes and describing
their OS/filesystem/Git/Python/shell/privilege baseline.

### Goal
Run non-destructive probes against both operator-managed Windows hosts, retain
ignored raw evidence and publish only generic host IDs plus sanitized
capability outcomes.

### Scope
- Two-host sanitized support matrix and compatibility notes.
- Evidence references for SSH access, non-interactive execution, fixture
  transfer and disposable root setup.
- Public-surface scan for tracked outputs.

### Acceptance
- Both hosts have recorded sanitized OS, filesystem, Git, Python, shell and
  privilege capabilities.
- SSH, non-interactive command execution and safe fixture transfer are checked.
- Tracked report excludes raw hostname, username, private paths and
  credentials.

### Depends On
- `establish-windows-lab-protocol`

### Related
- `openspec/changes/archive/2026-08-02-capture-windows-support-matrix/`

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `docs/compatibility.md`
- `openspec/changes/archive/2026-08-02-establish-windows-lab-protocol/`
- `openspec/changes/archive/2026-08-02-capture-windows-support-matrix/`

## Result
Implementation verified and OpenSpec changes archived; independent review
pending.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z карточка создана для controlled Windows research.
- 2026-08-02T00:58:19Z readiness pass после `020` нашел clean Linux baseline,
  но не нашел локальный Windows host inventory; карточка остается в backlog.
- 2026-08-02T05:48:42Z operator provided two Windows SSH targets in ignored
  inventory; SSH/Git/Python prerequisite confirmed on both hosts without
  recording host identities in tracked files.
- 2026-08-02T05:57:06Z `$changerail-deliver` начал fast-forward planning:
  добавлены ordered changes `establish-windows-lab-protocol` и
  `capture-windows-support-matrix`.
- 2026-08-02T05:57:06Z fast-forward завершен: OpenSpec artifacts для обоих
  changes созданы и прошли validation; карточка переведена в `3.inprogress`.
- 2026-08-02T06:09:58Z live Windows lab probe прошел на `windows-host-a` и
  `windows-host-b`; raw host output retained under ignored `.runtime/`, tracked
  compatibility matrix содержит только sanitized generic host ids.
- 2026-08-02T06:09:58Z оба текущих SSH session token reported
  `elevated=true`; harness не запрашивал UAC, `runas` или persistent elevation,
  future elevated-sensitive probes require separate operator action.
- 2026-08-02T06:13:39Z delivery завершил sync/archive для
  `establish-windows-lab-protocol` и `capture-windows-support-matrix`; карточка
  оставлена в `3.inprogress` до fresh independent review.
- 2026-08-02T06:23:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
