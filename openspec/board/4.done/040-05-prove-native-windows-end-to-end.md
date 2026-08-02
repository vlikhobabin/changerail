# Доказать native Windows support end-to-end

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`040-native-windows-implementation`

## Series Index
`05`

## Planning State
apply-ready after internal `ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `040-04-add-windows-automated-smoke`

## Summary
На обоих Windows hosts пройти clean-clone consumer lifecycle through native
`.cmd` entrypoints, generated-copy default wiring, verify/drift, scoped
delivery smoke, update/refresh and final compatibility documentation.

## Acceptance
- Both hosts start from a clean disposable clone without manual source edits.
- Native `.cmd` entrypoints, bootstrap and `verify-project` pass in generated
  project-local default mode without requiring Developer Mode or administrator
  elevation, or the support claim records an explicit blocker.
- Agent skill/command discovery confirms required Windows surfaces.
- Scoped no-push delivery smoke uses explicit staging scope and does not touch
  unrelated/runtime files.
- ChangeRail update preserves generated wiring contract or produces documented
  refresh/migration steps.
- Final compatibility matrix and migration guide are based on retained
  sanitized evidence.
- Windows smoke matrix and full Linux release baseline remain green.
- Public-surface current and history scans pass before release claim.

## Depends On
- `040-04-add-windows-automated-smoke`
- Серия `020-one-command-delivery-experience` завершена.

## Change Set
- `openspec/changes/prove-windows-clean-clone-lifecycle/`
- `openspec/changes/publish-windows-support-claim/`

## Verify
- Two-host end-to-end report with sanitized evidence.
- Windows smoke matrix.
- Full Linux release baseline and public-surface current/history scans.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/2.todo/040-04-add-windows-automated-smoke.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/consumer-adoption-runbook.md`

## Change 1: `prove-windows-clean-clone-lifecycle`

### Why
The final support claim needs a clean-clone proof on both native Windows hosts,
not only isolated unit and smoke coverage.

### Goal
Run and retain sanitized evidence for a disposable clean-clone lifecycle using
native `.cmd` entrypoints, generated-copy wiring, verify/drift and scoped
delivery smoke.

### Acceptance
- Both hosts complete the lifecycle or record an explicit support blocker.
- Skill/command discovery is included in the proof.
- No-push delivery smoke uses explicit staging scope and leaves runtime files
  out of tracked state.

### Depends On
- `040-04-add-windows-automated-smoke`

### Related
- `openspec/changes/prove-windows-clean-clone-lifecycle/`

## Change 2: `publish-windows-support-claim`

### Why
The public compatibility and migration docs must reflect actual retained
evidence before ChangeRail claims native Windows support.

### Goal
Update compatibility, migration and adoption docs from the two-host evidence
and final Linux release baseline.

### Acceptance
- Compatibility matrix and migration guide match retained sanitized evidence.
- Windows smoke matrix and Linux release baseline are green.
- Public-surface current and history scans pass before support claim.

### Depends On
- `prove-windows-clean-clone-lifecycle`

### Related
- `openspec/changes/publish-windows-support-claim/`

## Result
Implementation delivered and OpenSpec changes archived:

- `bin/bootstrap-project.cmd` added and generated-copy Windows helper inventory
  now includes `bootstrap-project(.cmd)`.
- Native Windows bootstrap selects `verify-project.cmd`; `verify-project`
  selects `openspec.cmd` for OpenSpec validation.
- Added `scripts/windows-clean-clone-lifecycle.py` and wired it into
  `scripts/smoke-windows-matrix.py --live`.
- Updated compatibility, migration, adoption, release and wiring docs with the
  retained evidence and explicit support blocker.

Final live evidence:

```text
aggregate live matrix report: .runtime/changerail/windows-smoke/20260802T133725Z-1ed04029/report.json
focused clean-clone report: .runtime/changerail/windows-clean-clone-lifecycle/040-05-after-openspec-handoff/report.json
local matrix report: .runtime/changerail/windows-smoke/20260802T134151Z-d6ad9e0f/report.json
release baseline: python3 scripts/run-release-baseline.py -> pass (30/30)
```

Support claim outcome: no full two-host native Windows support claim yet.
`windows-host-a` is blocked by missing Python `jsonschema` and missing
Node/npm/npx. `windows-host-b` passes clean clone and `.cmd` launch, but is
blocked by missing `npm` for MCP npm integrity verification during
generated-copy bootstrap. Both blockers are recorded in `docs/compatibility.md`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z provisional exit-gate card создана для двух Windows hosts.
- 2026-08-02T07:27:00Z refreshed against `030-03`: end-to-end proof must consume
  implemented `.cmd`, generated wiring, verifier/drift/Git safety and smoke
  matrix.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
- 2026-08-02T13:20:00Z internal `ff` создал apply-ready artifacts для
  `prove-windows-clean-clone-lifecycle` и `publish-windows-support-claim`;
  OpenSpec validation and whitespace checks passed; карточка переведена в
  `3.inprogress`.
- 2026-08-02T13:54:18Z implementation delivered; live matrix retained explicit
  Windows host prerequisite blockers; local matrix, release baseline, OpenSpec
  validation and diff checks passed; OpenSpec changes archived.
- 2026-08-02T14:18:38Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
