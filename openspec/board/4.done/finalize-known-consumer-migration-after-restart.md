# Завершить миграцию known consumers после restart gate

## Status
4.done

## Owner
operator + agent

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
- Five selected local consumer repositories were migrated or adopted to the
  ChangeRail wiring surface.
- Canonical and short command surfaces were made available where applicable:
  `/changerail:*`, `/chrl:*`, `$changerail-*` and `$chrl-*`.
- Stale generic OPSX command, skill and helper wiring was removed where
  applicable.
- Consumer repository changes were committed and pushed one repository at a
  time. Concrete names, paths and commit ids are retained only in ignored
  operator inventory.

## Verify
- Fresh read-only agent context checked each selected consumer.
- Each selected consumer passed:

```bash
/opt/changerail/bin/verify-project <project>
```

with `summary: pass (39/39 passed)`.
- Staged migration/adoption diffs passed `git diff --check` /
  `git diff --cached --check` before publication.
- Final public ChangeRail tracked files for this card do not contain real
  consumer project names or paths.

## Archive
- No OpenSpec change artifacts were created for this operational rollout.

## Related
- `openspec/board/3.inprogress/rename-opsx-to-changerail.md`
- `internal/changerail-consumer-inventory.md` (machine-local, ignored)
- `openspec/board/1.backlog/restart-stale-consumer-agent-sessions-before-next-work.md`

## Result
Completed for repository wiring, verification, commit and push across the
selected consumer set. One stale interactive session family was still visible at
final process scan; it was not stopped by this run and is split into a follow-up
housekeeping card. No migrated command surface was invoked from that stale
session during this rollout.

## Next
- Restart any still-running old consumer agent sessions before resuming active
  development in those sessions.

## Change Plan Notes
Per-consumer operational details, commit ids and local dirty-state notes live in
ignored `internal/`.

## Log
- 2026-07-12T07:35:47Z card created to defer session-dependent consumer
  migration after the main ChangeRail rename.
- 2026-07-12T09:20:17Z selected consumer repositories verified from a fresh
  read-only context, committed and pushed one repository at a time.
- 2026-07-12T09:20:17Z stale interactive session cleanup split into a follow-up
  housekeeping card because this run did not force-stop operator sessions.
