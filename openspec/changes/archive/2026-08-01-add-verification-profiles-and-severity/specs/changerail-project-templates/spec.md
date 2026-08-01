## ADDED Requirements

### Requirement: Project templates expose verification profile policy
Project templates MUST expose a public-safe verification profile policy in
generated consumer OpenSpec config.
The template MUST preserve strict all-surfaces behavior by default and document
only generic examples for optional or forbidden surfaces.

#### Scenario: Template renders default verification profile
- **WHEN** bootstrap renders `templates/project/openspec/config.yaml.tpl`
- **THEN** the generated `openspec/config.yaml` includes a strict default
  profile for Codex, Claude and legacy MCP surfaces
- **AND** it contains no private workspace names, credentials or runtime state

#### Scenario: Template documents non-blocking diagnostics
- **WHEN** generated consumer guidance is read
- **THEN** it describes that only explicitly non-blocking diagnostics can
  produce `pass-with-diagnostics`
- **AND** it does not describe project-wide baseline debt as silently green
