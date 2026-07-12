# ChangeRail project template

Этот каталог является source of truth для `bin/bootstrap-project`.
Bootstrap рендерит все файлы `*.tpl`, удаляет суффикс `.tpl` в целевом
проекте, копирует остальные файлы как skeleton и создает symlink-и на ChangeRail
surface.

## Placeholders

- `{{PROJECT_PATH}}` - абсолютный путь проекта-потребителя, например
  `/opt/example-project`.
- `{{PROJECT_NAME}}` - человекочитаемое имя проекта, например
  `example-project`.
- `{{PROJECT_KIND}}` - тип проекта, например `generic`.
- `{{CHANGERAIL_ROOT}}` - путь к ChangeRail source of truth, обычно `/opt/changerail`.
- `{{CHANGERAIL_SHARED_AGENTS}}` - generated copy of `AGENTS.shared.md`.

## Generated Files

Bootstrap generates project-local files:

- `AGENTS.md`
- `CLAUDE.md`
- `.gitignore`
- `.mcp.json`
- `.codex/config.toml`
- `openspec/config.yaml`
- `openspec/board/README.md`

Bootstrap creates symlink-и for shared ChangeRail surfaces instead of templating
them:

- `.claude/commands/changerail`
- `.claude/commands/chrl`
- `.claude/skills`
- `.codex/skills/changerail-*`
- `.codex/skills/chrl-*`
- `.codex/skills/openspec-*`
- `bin/openspec`
- `bin/changerail-review-verdict`

Runtime/auth paths remain ignored in generated `.gitignore`; bootstrap smoke
projects and reports stay under `.runtime`.
