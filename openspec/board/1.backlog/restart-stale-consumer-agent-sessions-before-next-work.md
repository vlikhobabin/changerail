# Restart stale consumer agent sessions before next work

## Status
1.backlog

## Owner
operator

## OpenSpec Stage
story

## Source
- Follow-up from
  `openspec/board/4.done/finalize-known-consumer-migration-after-restart.md`.

## Summary
Before resuming active development in any old consumer agent session that was
started before the ChangeRail wiring rollout, restart that session so it reloads
the current `/changerail:*`, `/chrl:*`, `$changerail-*` and `$chrl-*` surfaces.
Concrete consumer names, paths and process ids stay in ignored operator
inventory.

## Acceptance
- Stale pre-rollout consumer agent sessions are stopped or replaced with fresh
  sessions before they are used for development.
- Fresh sessions discover the current ChangeRail command and skill surfaces.
- Selected consumers still pass `/opt/changerail/bin/verify-project <project>`
  after restart.
- No real consumer project names, paths or process ids are committed to public
  ChangeRail tracked files.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `internal/changerail-consumer-inventory.md` (machine-local, ignored)

## Result
not started

## Next
- Restart stale consumer agent sessions when it is operationally safe.

## Log
- 2026-07-12T09:20:17Z card created after repository migration completed while
  one stale interactive session family was still visible in local process scan.
