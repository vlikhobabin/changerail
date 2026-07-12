# Завершить миграцию known consumers после restart gate

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Follow-up from `openspec/board/3.inprogress/rename-opsx-to-changerail.md`.
- Operator decision: publish the main ChangeRail rename now and finish
  session-dependent consumer migration later.

## Summary
Довести отложенную операционную часть миграции известных local consumers:
перезапустить активные Claude/Codex sessions после ChangeRail rewiring,
проверить, что новые `/changerail:*` и `$changerail-*` surfaces обнаруживаются
в свежем контексте, и затем зафиксировать consumer repository changes по
проектам. Реальные consumer names/paths остаются только в ignored operator
inventory.

## Acceptance
- Active Claude/Codex sessions in selected consumers are stopped or restarted
  before using `/changerail:*` or `$changerail-*`.
- Each selected consumer is checked from a fresh agent context after restart.
- Each selected consumer still passes `/opt/changerail/bin/verify-project
  <project>`.
- Consumer repository changes are reviewed and committed/pushed per owning
  repository policy, one project at a time.
- No real consumer project names or paths are committed to public ChangeRail
  tracked files.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `openspec/board/3.inprogress/rename-opsx-to-changerail.md`
- `internal/changerail-consumer-inventory.md` (machine-local, ignored)

## Result
not started

## Next
- Wait until active consumer sessions can be safely stopped or restarted.
- Run ChangeRail planning for this card when the operator is ready to finish
  consumer repository migration.

## Change Plan Notes
When this card is accepted, decompose it into per-consumer operational changes
without committing real consumer names or paths to public ChangeRail files.
Concrete order and status live in ignored `internal/`.

## Log
- 2026-07-12T07:35:47Z card created to defer session-dependent consumer
  migration after the main ChangeRail rename.
