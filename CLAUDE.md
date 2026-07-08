@AGENTS.md

# Claude Code — OPSX workspace notes

Этот файл — точка входа Claude Code в репозиторий OPSX. Агент-нейтральные
рабочие правила — в [`AGENTS.md`](AGENTS.md) (импортирован выше): Codex читает
его напрямую, Claude получает тот же корпус через импорт. Здесь — только
Claude-специфика.

## Обвязка Claude в этом репозитории

| Что | Где | В git |
| --- | --- | --- |
| Разрешения (максимальные + generic deny) | `.claude/settings.json` | да |
| Включение MCP-серверов | `.claude/settings.local.json` (`enabledMcpjsonServers`) | нет (machine-local) |
| MCP baseline | `.mcp.json` — `filesystem` (scope `/opt/opsx`) + `context7` | да |

Baseline MCP намеренно минимальный. Provider-MCP других workspace сюда не
добавляются: OPSX — источник технологии, а не потребитель доменных сервисов.

## Тулчейн OPSX в этом репозитории

Публичные source-файлы для OPSX surface:

- `skills/opsx-explore/`;
- `skills/opsx-ff/`;
- `skills/opsx-do/`;
- `skills/opsx-review/`;
- `skills/opsx-pub/`;
- `skills/opsx-deliver/`;
- `skills/openspec-*`;
- `claude/commands/opsx/explore.md`;
- `claude/commands/opsx/ff.md`;
- `claude/commands/opsx/do.md`;
- `claude/commands/opsx/review.md`;
- `claude/commands/opsx/pub.md`;
- `claude/commands/opsx/deliver.md`;
- `bin/openspec`;
- `bin/opsx-review-verdict`;
- `schemas/opsx-*.schema.json`.

Repo-local slash-команды `/opsx:*` подключены через внутренние относительные
симлинки `.claude/skills -> ../skills` и
`.claude/commands/opsx -> ../../claude/commands/opsx`. Codex skills в
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
