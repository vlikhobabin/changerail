## ADDED Requirements

### Requirement: Maintenance starter templates cover first scan universe
Opt-in maintenance templates MUST include enough starter catalog and policy
content for the configured initial scan universe to be fully covered.

#### Scenario: Starter catalog covers maintenance configuration
- **WHEN** bootstrap renders a consumer with `--with-maintenance`
- **THEN** `.changerail/knowledge.yaml` contains active catalog records for `.changerail/knowledge.yaml` and `.changerail/maintenance.yaml`
- **AND** those records use repository-relative `source_globs` and public-safe owner metadata

#### Scenario: Starter catalog covers board template
- **WHEN** bootstrap renders a consumer with `--with-maintenance`
- **THEN** `.changerail/knowledge.yaml` contains an active `reference` catalog record for `openspec/board/card-template.md`
- **AND** the record points verification to generic project checks instead of a domain-specific taxonomy

### Requirement: Maintenance starter index is generated
Opt-in maintenance templates or bootstrap rendering MUST provide a current
generated knowledge index matching the rendered starter catalog and policy.

#### Scenario: Generated index matches rendered catalog
- **WHEN** bootstrap renders maintenance starter files
- **THEN** `.changerail/KNOWLEDGE.md` contains deterministic index content for the rendered catalog records
- **AND** `render-index --check` observes no drift before any operator edits

#### Scenario: Starter index remains public-safe
- **WHEN** generated maintenance starter files are scanned before commit
- **THEN** `.changerail/KNOWLEDGE.md` contains only repository-relative paths and generic public-safe text
- **AND** it contains no credentials, runtime report content or private workspace names
