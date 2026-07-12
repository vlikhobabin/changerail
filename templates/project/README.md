# ChangeRail project template

Этот каталог является source of truth для `bin/bootstrap-project`.
Bootstrap рендерит все файлы `*.tpl`, удаляет суффикс `.tpl` в целевом
проекте, копирует остальные файлы как skeleton и создает symlink-и на ChangeRail
surface.

## Placeholders

- `{{PROJECT_PATH}}` - абсолютный путь проекта-потребителя; используется только
  в explicit local config mode.
- `{{PROJECT_CONFIG_SCOPE}}` - tracked filesystem scope. Default portable
  value is `.`.
- `{{CODEX_PROJECT_KEY}}` - trusted project key for generated Codex config.
  Default portable value is `.`.
- `{{PROJECT_ROOT_LABEL}}` - human-readable project root label for tracked
  docs. Default portable value is `this repository`.
- `{{PROJECT_NAME}}` - человекочитаемое имя проекта, например
  `example-project`.
- `{{PROJECT_KIND}}` - тип проекта, например `generic`.
- `{{CHANGERAIL_ROOT}}` - путь к ChangeRail source of truth; used for symlink
  creation and explicit local config mode.
- `{{CHANGERAIL_ROOT_LABEL}}` - public-safe ChangeRail source label for
  tracked docs.
- `{{CHANGERAIL_SHARED_SOURCE}}` - marker value for generated shared AGENTS
  content.
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
- `bin/verify-project`
- `bin/changerail-review-verdict`

Runtime/auth paths remain ignored in generated `.gitignore`; bootstrap smoke
projects and reports stay under `.runtime`.
