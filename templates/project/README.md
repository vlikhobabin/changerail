# OPSX project template

Этот каталог является source of truth для `bin/bootstrap-project`.
Bootstrap рендерит все файлы `*.tpl`, удаляет суффикс `.tpl` в целевом
проекте, копирует остальные файлы как skeleton и создает symlink-и на OPSX
surface.

## Placeholders

- `{{PROJECT_PATH}}` - абсолютный путь проекта-потребителя, например
  `/opt/example-project`.
- `{{PROJECT_NAME}}` - человекочитаемое имя проекта, например
  `example-project`.
- `{{PROJECT_KIND}}` - тип проекта, например `generic`.
- `{{OPSX_ROOT}}` - путь к OPSX source of truth, обычно `/opt/opsx`.
- `{{OPSX_SHARED_AGENTS}}` - generated copy of `AGENTS.shared.md`.

## Generated Files

Bootstrap generates project-local files:

- `AGENTS.md`
- `CLAUDE.md`
- `.gitignore`
- `.mcp.json`
- `.codex/config.toml`
- `openspec/config.yaml`
- `openspec/board/README.md`

Bootstrap creates symlink-и for shared OPSX surfaces instead of templating
them:

- `.claude/commands/opsx`
- `.claude/skills`
- `.codex/skills/opsx-*`
- `.codex/skills/openspec-*`
- `bin/openspec`
- `bin/opsx-review-verdict`

Runtime/auth paths remain ignored in generated `.gitignore`; bootstrap smoke
projects and reports stay under `.runtime`.
