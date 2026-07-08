# Версионирование и релизная дисциплина (Фаза 6)

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- OPSX roadmap, раздел 12, Фаза 6 (`docs/opsx-source-of-truth-architecture.md`).
- Раздел 14 (риск always-latest symlink) и раздел 15 (открытые решения).

## Summary
Сделать OPSX самостоятельной поддерживаемой технологией: ввести semver,
changelog с breaking-маркерами, compatibility notes для Codex CLI, Claude Code и
OpenSpec CLI, migration notes между версиями и CI для templates, bootstrap,
verify и drift.

## Acceptance
- Введена и задокументирована semver-схема.
- Есть changelog с явными breaking-маркерами.
- Compatibility notes покрывают Codex CLI, Claude Code и OpenSpec CLI.
- Есть migration notes между версиями OPSX.
- CI прогоняет templates, bootstrap, verify, drift и wiring smoke; красно-зеленый.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `scripts/smoke-wiring-discovery.py`
- `bin/openspec` (compatibility pin из Фазы 1)

## Result
not started

## Next
- triage: после стабильных bootstrap/verify (Фаза 2) и drift gate (Фаза 3).

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.).

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 6 scope.
