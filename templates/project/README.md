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
- `{{PROJECT_PROFILE}}` - topology profile: `generic`, `workspace-root` или
  `service`; `{{PROJECT_KIND}}` сохраняется как compatibility placeholder.
- `{{SURFACES_PROFILE}}` - `all-surfaces` или `codex-only`.
- `{{CODEX_POLICY}}`, `{{CODEX_APPROVAL_POLICY}}` и
  `{{CODEX_SANDBOX_MODE}}` - объявленная Codex authority и ее TOML values.
- `{{CODEX_SURFACE_STATE}}`, `{{CLAUDE_SURFACE_STATE}}`,
  `{{LEGACY_MCP_SURFACE_STATE}}`, `{{LEGACY_ARTIFACTS_SURFACE_STATE}}` -
  tracked verification matrix.
- `{{TOPOLOGY_GUIDANCE}}`, `{{CODEX_AUTHORITY_GUIDANCE}}` - bounded guidance
  для выбранных профилей.
- `{{CHANGERAIL_ROOT}}` - путь к ChangeRail source of truth; used for symlink
  creation and explicit local config mode.
- `{{CHANGERAIL_ROOT_LABEL}}` - public-safe ChangeRail source label for
  tracked docs.
- `{{CHANGERAIL_SHARED_SOURCE}}` - marker value for generated shared AGENTS
  content.
- `{{CHANGERAIL_SHARED_AGENTS}}` - generated copy of `AGENTS.shared.md`.

Generated `openspec/config.yaml` records canonical bootstrap profiles and their
ChangeRail verification policy. `all-surfaces` требует Codex, Claude и legacy
MCP; `codex-only` оставляет Claude и legacy MCP optional. Ignored runtime state
must not be used to weaken verification.

## Generated Files

Bootstrap generates project-local files (`CLAUDE.md` only for
`all-surfaces`; `README.md` only with `--with-readme`):

- `AGENTS.md`
- `CLAUDE.md`
- `.gitignore`
- `.mcp.json`
- `.codex/config.toml`
- `openspec/config.yaml`
- `openspec/board/README.md`
- `README.md` (opt-in)

Bootstrap creates symlink-и for shared ChangeRail surfaces instead of templating
them; `.claude/*` wiring создается только для `all-surfaces`:

- `.claude/commands/changerail`
- `.claude/commands/chrl`
- `.claude/skills`
- `.codex/skills/changerail-*`
- `.codex/skills/chrl-*`
- `.codex/skills/openspec-*`
- `bin/openspec`
- `bin/changerail-python`
- `bin/changerail-delivery-manifest`
- `bin/verify-project`
- `bin/changerail-review-verdict`
- `bin/changerail-evidence`

Maintenance integration is opt-in. `bin/bootstrap-project --with-maintenance`
also renders:

- `.changerail/knowledge.yaml`
- `.changerail/maintenance.yaml`

and wires:

- `bin/changerail-maintenance`
- `bin/changerail-maintenance-runner`

Native Windows generated-copy wiring records those maintenance helpers and their
`.cmd` wrappers in `openspec/changerail-wiring.json` only when maintenance is
opted in.

## Consumer CI Opt-In

`bin/bootstrap-project --lock-enforcement strict --with-ci` additionally
renders `.github/workflows/changerail-consumer-verify.yml`. The workflow has
read-only repository permissions and does not run delivery or require Codex
auth.

The provider-neutral contract is: read and validate the strict
`openspec/changerail-consumer-lock.json`, install its exact public ChangeRail
revision into a disposable path, run lock-owned `--refresh-wiring`, then run
`bin/verify-project`, targeted/full OpenSpec validation and `git diff --check`.
Other CI providers should preserve this sequence and fail before repair when
the exact source revision is unavailable.

Runtime/auth paths remain ignored in generated `.gitignore`; bootstrap smoke
projects and reports stay under `.runtime`.

## Post-Bootstrap And Git

`--configure-existing` is a separate no-template mode for idempotent
`--link-codex-auth` and lock-owned POSIX `--refresh-wiring`. It refuses
project-owned destinations, undeclared links and unrelated Git dirty state.

`--init-git` may set `--default-branch` and configure `origin` through
`--remote`. It does not stage, commit, push or create remote repositories.
Remote credentials are rejected before target mutation and URLs are redacted
from bootstrap output.

## Static And Runtime Verification

Generated `.codex/config.toml` tracks `project_doc_max_bytes = 32768`.
`bin/verify-project .` measures `AGENTS.md` as UTF-8 bytes: below 85 percent is
PASS, 85 percent through the limit is a non-blocking warning, and over the
limit is blocking. Existing consumers without the key use the same documented
compatibility default until migrated.

Static verification does not prove the effective Codex process state. An
operator may run `bin/verify-project . --runtime-diagnostics` with the
project-local `CODEX_HOME`. Supported probes store raw output only under
ignored `.runtime/changerail/diagnostics/`; reports and docs may contain only
the redacted allowlisted summary.
