# Доказать native Windows support end-to-end

## Status
1.backlog

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`05`

## Planning State
refreshed after `030-03`; pending deliver-ready decomposition

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
- none yet; run `$changerail-ff` after `040-04`

## Verify
- Two-host end-to-end report with sanitized evidence.
- Windows smoke matrix.
- Full Linux release baseline and public-surface current/history scans.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/1.backlog/040-04-add-windows-automated-smoke.md`
- `openspec/board/3.inprogress/030-03-freeze-native-windows-architecture.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/consumer-adoption-runbook.md`

## Result
refreshed; implementation not started

## Next
- После publish `040-04`: `$changerail-ff openspec/board/1.backlog/040-05-prove-native-windows-end-to-end.md`

## Log
- 2026-08-01T15:07:29Z provisional exit-gate card создана для двух Windows hosts.
- 2026-08-02T07:27:00Z refreshed against `030-03`: end-to-end proof must consume
  implemented `.cmd`, generated wiring, verifier/drift/Git safety and smoke
  matrix.
