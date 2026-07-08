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

Публичные source-файлы для минимального OPSX surface уже есть:

- `skills/opsx-explore/`;
- `skills/opsx-ff/`;
- `claude/commands/opsx/explore.md`;
- `claude/commands/opsx/ff.md`.

Repo-local slash-команды `/opsx:*` здесь **пока не подключены** через
внутренние относительные симлинки `.claude/skills -> skills` и
`.claude/commands/opsx -> claude/commands/opsx`. Этот wiring нужно делать
отдельным проверяемым change с discovery-smoke для Claude и Codex.

Не подключай сюда внешние skills-источники симлинками: абсолютная ссылка на
другой workspace в публичном репозитории — это утечка machine-local пути.

## Напоминания

- Репозиторий публичный по умолчанию: перед каждым commit — review диффа на
  machine-local пути, реальные имена проектов и runtime-артефакты.
- Локальный миграционный контекст (реальные пути, инвентарь, порядок
  миграции) — только в `internal/local-migration-context.md`.
- Коммит и push — только по явной просьбе оператора.
