## Context

`/opt/opsx` is the public source of truth for reusable methodology, skills,
commands and helper wrappers. Consumer projects remain separate repositories
and should receive only project-local files plus symlink-и to OPSX-owned
surfaces.

## Decision

Add `templates/project/` as a tracked template tree. Template files use explicit
double-brace placeholders:

- `{{PROJECT_PATH}}`
- `{{PROJECT_NAME}}`
- `{{PROJECT_KIND}}`
- `{{OPSX_ROOT}}`
- `{{OPSX_SHARED_AGENTS}}`

Bootstrap will render every `*.tpl` file recursively and strip the `.tpl`
suffix in the generated project. Non-template files under
`templates/project/openspec/` are copied as skeleton source. Symlink-и are not
stored as template files because their targets depend on `{{OPSX_ROOT}}` and
are easier to verify when created by `bootstrap-project`.

## Template Surface

- `AGENTS.md.tpl`: project-local role, public safety and embedded OPSX
  methodology generated from `AGENTS.shared.md`.
- `CLAUDE.md.tpl`: concise Claude-facing pointer to `AGENTS.md` and OPSX
  command surface.
- `gitignore.tpl`: conservative runtime/auth ignores for consumer projects.
- `mcp.json.tpl`: project-scoped filesystem MCP plus Context7.
- `codex-config.toml.tpl`: trusted project path, project-scoped filesystem MCP
  and OPSX skill discovery defaults.
- `openspec/`: default `config.yaml`, board layout and `.gitkeep` placeholders.

## Public Safety

Templates may include `/opt/opsx` and `/opt/example-project` as documented
generic paths. They must not include private workspace names, customer data,
secrets, traces, sessions or machine-local runtime reports.

## Verification

This change is docs/template-only. Verification uses OpenSpec validation,
template syntax inspection, config parsing for rendered output through later
changes, and public-surface scans.
