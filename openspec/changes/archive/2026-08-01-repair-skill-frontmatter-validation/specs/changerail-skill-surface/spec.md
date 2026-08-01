## ADDED Requirements

### Requirement: Bundled skill frontmatter is valid YAML
ChangeRail bundled skills MUST have YAML-valid frontmatter metadata before they
are published as part of the generic skill surface.

#### Scenario: Maintainer validates bundled skills
- **WHEN** release verification inspects `skills/*/SKILL.md`
- **THEN** every skill frontmatter parses as a YAML mapping
- **AND** each parsed `name` value matches the bundled skill directory name

#### Scenario: Lifecycle skill description contains colon
- **WHEN** a lifecycle skill description needs text containing `: `
- **THEN** the frontmatter represents that value in a YAML-valid form such as a
  quoted scalar

### Requirement: Skill metadata validation is local and deterministic
ChangeRail skill metadata validation MUST NOT depend on networked Codex
discovery, live credentials or external agent runtime diagnostics.

#### Scenario: Release gate checks skills without Codex credentials
- **WHEN** the local release baseline validates skill metadata
- **THEN** it runs a repository-local parser check
- **AND** it can fail invalid frontmatter before any networked `codex exec`
  discovery attempt would be needed
