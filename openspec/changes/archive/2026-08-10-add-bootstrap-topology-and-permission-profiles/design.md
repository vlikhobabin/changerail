## Context

`bin/bootstrap-project` сейчас принимает свободный `--kind`, подставляет его в
docs и всегда рендерит один template set. `openspec/config.yaml` получает strict
all-surfaces policy, а `.codex/config.toml` всегда включает unattended full
access. Verifier уже умеет required/optional/forbidden surfaces, поэтому новый
bootstrap contract должен переиспользовать эту модель, а не вводить второй
profile parser.

## Goals / Non-Goals

**Goals:**
- сделать topology, surface и Codex authority observable tracked choices;
- выбрать безопасный public default;
- сохранить legacy all-surfaces consumers и `--kind generic`;
- проверить всю matrix до записи target.

**Non-Goals:**
- генерировать application/domain source code;
- менять runtime authority существующих consumers автоматически;
- ослаблять mandatory OpenSpec или source-wiring checks.

## Decisions

### Три независимые оси выбора

Bootstrap получает `--profile generic|workspace-root|service`,
`--surfaces all-surfaces|codex-only` и
`--codex-policy safe-interactive|trusted-automation`. Один typed profile model
используется renderer-ом, verifier-ом и smoke fixtures.

Альтернатива с одним составным preset отклонена: она связывает topology и agent
authority и быстро создает комбинаторные aliases.

### Safe interactive default

Default рендерит `approval_policy = "on-request"` и
`sandbox_mode = "workspace-write"`. `trusted-automation` рендерит существующие
`never`/`danger-full-access`, но только после explicit flag. Dry-run печатает
выбранную policy до mutation.

### Surface compatibility

`all-surfaces` остается default и сохраняет текущие required Codex/Claude/MCP
surfaces. `codex-only` оставляет Codex required, Claude optional, legacy MCP
optional и legacy artifacts forbidden. Mandatory targeted validation не зависит
от surface profile.

### Topology profiles

`generic` сохраняет текущий neutral skeleton. `workspace-root` добавляет
aggregator ownership guidance и не создает child repositories. `service`
фиксирует single-repository ownership и delivery guidance, но не создает
service-specific code или deployment config.

### Legacy `--kind`

`--kind` временно принимается как alias `--profile`. Одновременные
конфликтующие values и unknown names останавливают bootstrap до target mutation.
Generated docs используют только canonical `profile` terminology.

## Risks / Trade-offs

- [Default authority change affects automation scripts] -> automation обязана
  передать `--codex-policy trusted-automation`; compatibility docs и smoke
  фиксируют migration.
- [Profile matrix drifts between renderer and verifier] -> один normalized model
  и table-driven smoke являются source of truth.
- [Workspace/service presets become domain generators] -> specs ограничивают их
  ownership guidance и project policy.

## Migration Plan

1. Добавить normalized profile model и fail-before-write parsing.
2. Обновить templates и verifier.
3. Добавить matrix smoke и docs.
4. Existing generated consumers не переписывать; новые defaults действуют
   только на future bootstrap/configure selections.

## Open Questions

- none
