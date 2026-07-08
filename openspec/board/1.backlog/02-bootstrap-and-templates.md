# Bootstrap и templates (Фаза 2)

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- OPSX roadmap, раздел 12, Фаза 2 (`docs/opsx-source-of-truth-architecture.md`).
- Разделы 10 (Bootstrap) и 11 (Verification и drift).

## Summary
Дать возможность создавать новый проект-потребитель одной командой: собрать
`templates/project`, реализовать `bin/bootstrap-project` и красно-зеленый gate
`bin/verify-project`, проверить всё на smoke-проекте в ignored `.runtime`.

## Acceptance
- `templates/project/` содержит `AGENTS.md.tpl`, `CLAUDE.md.tpl`, `gitignore.tpl`,
  `mcp.json.tpl`, `codex-config.toml.tpl` и `openspec/` заготовку.
- Placeholders для project path, project name и project kind задокументированы.
- `bin/verify-project <path>` — красно-зеленый gate (exit-код), проверяет
  symlink-и, разрешаемость в OPSX (прямо или через aggregator), `openspec/config.yaml`,
  `openspec validate --all`, MCP/Codex scope, достижимость контрактов/schemas и
  игнор runtime/auth путей.
- `bin/bootstrap-project` создает каталоги, symlink-и и generated файлы,
  refuse-on-existing по умолчанию, поддерживает dry-run/backup и запускает
  `verify-project`.
- Smoke-проект под `.runtime` проверяет bootstrap end-to-end и не коммитится.
- Public examples остаются generic (`/opt/example-project`).

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `docs/wiring-discovery.md`
- `scripts/smoke-wiring-discovery.py`

## Result
not started

## Next
- triage: после Фазы 1 (контракты/helper достижимы для verify). Через `opsx-ff`
  разложить на changes (ориентировочно: templates; verify-project; bootstrap-project
  + smoke).

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.).

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 2 scope.
