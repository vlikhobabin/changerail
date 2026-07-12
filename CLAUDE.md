@AGENTS.md

# Claude Code — ChangeRail workspace notes

Этот файл — точка входа Claude Code в репозиторий ChangeRail. Агент-нейтральные
рабочие правила — в [`AGENTS.md`](AGENTS.md) (импортирован выше): Codex читает
его напрямую, Claude получает тот же корпус через импорт. Здесь — только
Claude-специфика.

## Обвязка Claude в этом репозитории

| Что | Где | В git |
| --- | --- | --- |
| Разрешения (максимальные + generic deny) | `.claude/settings.json` | да |
| Включение MCP-серверов | `.claude/settings.local.json` (`enabledMcpjsonServers`) | нет (machine-local) |
| MCP baseline | `.mcp.json` — `filesystem` (scope `/opt/changerail`) + `context7` | да |

Baseline MCP намеренно минимальный. Provider-MCP других workspace сюда не
добавляются: ChangeRail — источник технологии, а не потребитель доменных сервисов.

## Тулчейн ChangeRail в этом репозитории

Публичные source-файлы для ChangeRail surface:

- `skills/changerail-explore/`;
- `skills/changerail-ff/`;
- `skills/changerail-do/`;
- `skills/changerail-review/`;
- `skills/changerail-pub/`;
- `skills/changerail-deliver/`;
- `skills/openspec-*`;
- `claude/commands/changerail/explore.md`;
- `claude/commands/changerail/ff.md`;
- `claude/commands/changerail/do.md`;
- `claude/commands/changerail/review.md`;
- `claude/commands/changerail/pub.md`;
- `claude/commands/changerail/deliver.md`;
- `bin/openspec`;
- `bin/changerail-review-verdict`;
- `schemas/changerail-*.schema.json`.

Repo-local slash-команды `/changerail:*` подключены через внутренние относительные
симлинки `.claude/skills -> ../skills` и
`.claude/commands/changerail -> ../../claude/commands/changerail`. Codex skills в
`.codex/skills/` также являются относительными symlink-и на source directories
под `skills/`.

Не подключай сюда внешние skills-источники симлинками: абсолютная ссылка на
другой workspace в публичном репозитории — это утечка machine-local пути.

## Напоминания

- Репозиторий публичный по умолчанию: перед каждым commit — review диффа на
  machine-local пути, реальные имена проектов и runtime-артефакты.
- Локальный миграционный контекст (реальные пути, инвентарь, порядок
  миграции) — только в `internal/local-migration-context.md`.
- Коммит и push — только по явной просьбе оператора.
