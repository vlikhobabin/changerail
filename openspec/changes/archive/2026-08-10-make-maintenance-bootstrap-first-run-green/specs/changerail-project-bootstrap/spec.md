## ADDED Requirements

### Requirement: Maintenance opt-in first run is green
Bootstrap MUST make a fresh `--with-maintenance` consumer immediately usable for
the deterministic maintenance first-run checks without manual edits.

#### Scenario: Fresh maintenance consumer validates and scans
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name example-project --kind generic --with-maintenance`
- **THEN** the target receives `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` and `.changerail/KNOWLEDGE.md`
- **AND** `./bin/changerail-maintenance validate-catalog --json` exits zero in the generated target
- **AND** `./bin/changerail-maintenance render-index --check` exits zero in the generated target
- **AND** `./bin/changerail-maintenance scan --json` exits zero without threshold-reaching findings in the generated target

#### Scenario: Default bootstrap remains maintenance-free
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name example-project --kind generic` without `--with-maintenance`
- **THEN** bootstrap does not create `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` or `.changerail/KNOWLEDGE.md`
- **AND** the target continues to pass the existing non-maintenance verification baseline

### Requirement: Maintenance refresh preserves project-owned catalog policy
Bootstrap refresh behavior for maintenance opt-in MUST NOT silently overwrite
project-owned catalog or policy customization.

#### Scenario: Generated index can refresh
- **WHEN** a generated maintenance index is stale and remains generated-owned
- **THEN** the supported refresh path can update `.changerail/KNOWLEDGE.md`
- **AND** the refreshed output is deterministic and repository-relative

#### Scenario: Project-owned catalog customization is preserved
- **WHEN** a consumer has changed `.changerail/knowledge.yaml` or `.changerail/maintenance.yaml`
- **THEN** bootstrap or refresh refuses to overwrite that customization silently
- **AND** diagnostics identify the required operator action without printing private paths or runtime data
