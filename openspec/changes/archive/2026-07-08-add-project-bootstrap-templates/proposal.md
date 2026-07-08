## Why

Новые OPSX consumers должны получать одинаковый public-safe project skeleton
без ручного копирования agent instructions, MCP/Codex config и OpenSpec board
layout. Шаблоны нужны до `bootstrap-project`, чтобы генерация имела явный
source of truth.

## What Changes

- Добавить `templates/project/` для generic consumer project.
- Зафиксировать placeholders для project path, project name и project kind.
- Добавить OpenSpec skeleton, который bootstrap сможет копировать в consumer
  repository.
- Документировать generated files, symlink responsibilities и ignored
  runtime/auth paths.

## Capabilities

### New Capabilities
- `opsx-project-templates`: reusable project templates and placeholder contract
  for OPSX consumer bootstrap.

### Modified Capabilities
- none

## Impact

- Affected files: `templates/project/**`, `README.md`,
  `docs/opsx-source-of-truth-architecture.md`, `openspec/specs/**`.
- Consumer projects get generated project files from tracked OPSX templates.
- No runtime reports, secrets or local machine state are committed.
