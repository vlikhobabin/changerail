# changerail-project-templates Specification

## Purpose
Зафиксировать tracked project template surface, который ChangeRail использует для
создания новых consumer repositories без ручного копирования agent rules,
OpenSpec board и MCP/Codex config.
## Requirements
### Requirement: Project template set
ChangeRail MUST provide a tracked `templates/project/` tree for bootstrapping
generic consumer projects.

#### Scenario: Maintainer inspects project templates
- **WHEN** the `templates/project/` directory is listed
- **THEN** it contains `AGENTS.md.tpl`, `CLAUDE.md.tpl`, `gitignore.tpl`,
  `mcp.json.tpl`, `codex-config.toml.tpl` and an `openspec/` skeleton

### Requirement: Placeholder contract
Project templates MUST document and use stable placeholders for project path,
project name and project kind.
Project templates MUST separate portable tracked scope placeholders from
machine-local absolute path placeholders.

#### Scenario: Bootstrap renders project-local files
- **WHEN** `bootstrap-project` renders templates for `/opt/example-project`
- **THEN** generated project files contain the rendered project path, project
  name and project kind instead of raw placeholder tokens

#### Scenario: Bootstrap renders portable project-local files
- **WHEN** bootstrap renders templates in the default config mode
- **THEN** generated tracked files avoid raw absolute consumer project paths
- **AND** project-local config still scopes filesystem access to the generated
  repository

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
Project templates MUST pin automatically executed npm MCP dependencies to exact
versions represented in a tracked integrity lock that is verified during trusted
setup.

#### Scenario: Public-surface scan covers templates
- **WHEN** templates are prepared for commit
- **THEN** scan output contains only generic examples such as `/opt/changerail` and
  `/opt/example-project`

#### Scenario: Generated MCP dependencies are exact-version pinned
- **WHEN** project templates render `.mcp.json` and `.codex/config.toml`
- **THEN** every automatically executed npm MCP package argument includes an
  exact version
- **AND** the package/version is represented in the tracked MCP npm integrity
  lock
- **AND** `verify-project` can compare that lock entry with npm registry
  `dist.integrity`

### Requirement: Templates render ChangeRail placeholders
Project templates MUST use ChangeRail placeholder names and generated prose
after the rename.

#### Scenario: Template is rendered
- **WHEN** bootstrap renders project templates
- **THEN** placeholders such as `{{CHANGERAIL_ROOT}}` are resolved to the
  configured ChangeRail source-of-truth path
- **AND** generated `AGENTS.md` and `CLAUDE.md` refer to ChangeRail, not OPSX,
  except explicit migration notes

#### Scenario: Claude command list is generated
- **WHEN** `CLAUDE.md` is generated for a consumer project
- **THEN** it lists `/changerail:*` lifecycle commands

### Requirement: Consumer board templates expose current workflow guidance
Project board templates MUST give generated consumers the current ChangeRail
card lifecycle and a canonical pointer to reusable workflow guidance.

#### Scenario: Consumer board README is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the project
  board README
- **THEN** the generated file describes the `1.backlog -> 2.todo ->
  3.inprogress -> 4.done` review-gated lifecycle
- **AND** it points maintainers to the canonical ChangeRail guide or shared
  methodology for the orchestrator, worker and independent reviewer model

#### Scenario: Template content is reviewed for public safety
- **WHEN** project templates are scanned before commit
- **THEN** workflow examples use generic ChangeRail paths such as
  `/opt/changerail` and `/opt/example-project`

### Requirement: Generated workflow guidance remains testable
Project templates MUST render workflow guidance in stable enough terms for
bootstrap smoke to detect lifecycle and review-gated board semantics.

#### Scenario: Consumer project is generated
- **WHEN** bootstrap renders `AGENTS.md` and `openspec/board/README.md`
- **THEN** generated text includes the ChangeRail lifecycle, role model,
  independent review gate and `3.inprogress -> 4.done` finalization boundary

### Requirement: Generated consumers receive fix-budget recovery guidance
Project templates MUST explain the distinction between implementation fix
cycles and independent-review rescue cycles and MUST retain the shared
autonomous recovery branches.

#### Scenario: Consumer AGENTS guidance is generated
- **WHEN** bootstrap renders `AGENTS.md` for a consumer project
- **THEN** generated guidance identifies `max-fix-cycles` as a pre-review
  implement/verify bound and `max-review-cycles` as a post-review rescue bound
- **AND** it names `fix_budget_exhausted` as a non-delivered handoff

#### Scenario: Generated agent chooses recovery scope
- **WHEN** a generated consumer agent reads the delivery rules after fix-budget
  exhaustion
- **THEN** it is directed to choose bounded same-card micro-fix, linked
  rescue/replacement card or external blocker according to observable scope
- **AND** manual exceptional budget is not described as the default path
