# Доказать native Windows support end-to-end

## Status
2.todo

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`05`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

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
- `openspec/changes/prove-windows-clean-clone-lifecycle/` (planned)
- `openspec/changes/publish-windows-support-claim/` (planned)

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
ready for `$chrl-deliver`

## Next
- Выполнять после `040-04` в tracked runner plan
  `040-native-windows-implementation`.

## Log
- 2026-08-01T15:07:29Z provisional exit-gate card создана для двух Windows hosts.
- 2026-08-02T07:27:00Z refreshed against `030-03`: end-to-end proof must consume
  implemented `.cmd`, generated wiring, verifier/drift/Git safety and smoke
  matrix.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
