## Why

Некоторые bundled ChangeRail skills содержат YAML frontmatter с некавыченым
scalar, в котором есть `: `. Такой файл может быть пропущен Codex skill
discovery, а текущий deterministic smoke проверяет только строку `name` и не
ловит этот класс регрессии.

## What Changes

- Исправить frontmatter canonical lifecycle skills, чтобы metadata была
  YAML-valid.
- Усилить wiring discovery smoke: он должен парсить полный frontmatter bundled
  skills настоящим YAML parser-ом, проверять `name` и детерминированно
  отклонять negative fixture с некавыченым `: `.
- Добавить release baseline requirement и зависимость, чтобы локальный baseline
  и CI запускали тот же parser path без сетевого `codex exec` и без реальных
  credentials.
- Обновить OpenSpec requirements для skill metadata, wiring discovery и release
  CI gate.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-skill-surface`: bundled lifecycle skill metadata должна быть
  валидным YAML frontmatter, пригодным для agent discovery.
- `changerail-wiring-discovery`: wiring smoke должен проверять полный YAML
  frontmatter всех bundled skills и negative fixture.
- `changerail-release-ci`: release baseline должен включать deterministic skill
  frontmatter validation как обязательный локальный и CI gate.

## Impact

- `skills/*/SKILL.md` frontmatter.
- `scripts/smoke-wiring-discovery.py` и release baseline dependency set.
- `openspec/specs/*` после sync delta specs.
- No networked Codex discovery call is introduced; checks stay local and
  deterministic.
