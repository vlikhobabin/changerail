# opsx-project-templates Specification

## Purpose
Зафиксировать tracked project template surface, который OPSX использует для
создания новых consumer repositories без ручного копирования agent rules,
OpenSpec board и MCP/Codex config.

## Requirements
### Requirement: Project template set
OPSX MUST provide a tracked `templates/project/` tree for bootstrapping
generic consumer projects.

#### Scenario: Maintainer inspects project templates
- **WHEN** the `templates/project/` directory is listed
- **THEN** it contains `AGENTS.md.tpl`, `CLAUDE.md.tpl`, `gitignore.tpl`,
  `mcp.json.tpl`, `codex-config.toml.tpl` and an `openspec/` skeleton

### Requirement: Placeholder contract
Project templates MUST document and use stable placeholders for project path,
project name and project kind.

#### Scenario: Bootstrap renders project-local files
- **WHEN** `bootstrap-project` renders templates for `/opt/example-project`
- **THEN** generated project files contain the rendered project path, project
  name and project kind instead of raw placeholder tokens

### Requirement: OpenSpec skeleton
Project templates MUST include a minimal OpenSpec skeleton suitable for a new
consumer repository.

#### Scenario: New project receives OpenSpec layout
- **WHEN** a project is generated from `templates/project/`
- **THEN** it has `openspec/config.yaml`, board columns, `openspec/changes/`
  and `openspec/specs/`

### Requirement: Public-safe template content
Project templates MUST avoid private workspace names, customer data, secrets,
local traces, credentials and runtime reports.

#### Scenario: Public-surface scan covers templates
- **WHEN** templates are prepared for commit
- **THEN** scan output contains only generic examples such as `/opt/opsx` and
  `/opt/example-project`
