## ADDED Requirements

### Requirement: Maintenance template surface is opt-in
Project templates MUST include maintenance policy, catalog and ignore snippets
only through explicit maintenance opt-in rendering.

#### Scenario: Opted-in template is rendered
- **WHEN** bootstrap renders a consumer with `--with-maintenance`
- **THEN** generated tracked maintenance files use public-safe generic
  placeholders and repository-relative paths
- **AND** generated ignored runtime rules cover `.runtime/changerail/maintenance/`

#### Scenario: Non-opted-in template is rendered
- **WHEN** bootstrap renders a consumer without `--with-maintenance`
- **THEN** generated tracked files do not contain maintenance policy skeletons
  or scheduler examples
- **AND** existing template smoke expectations remain valid

### Requirement: Maintenance generated-copy ownership
Project templates MUST allow generated Windows wiring manifests to record
maintenance helper copies as generated-owned artifacts.

#### Scenario: Maintenance helper copy is generated
- **WHEN** native Windows bootstrap writes a maintenance helper copy for an
  opted-in consumer
- **THEN** the generated ownership metadata records the project-relative target
  path, source identity and digest
- **AND** later refresh can update that generated-owned helper without
  overwriting project-owned files

#### Scenario: Maintenance example paths stay public-safe
- **WHEN** template and example files are scanned before commit
- **THEN** maintenance examples use generic paths such as `/opt/changerail` and
  `/opt/example-project`
- **AND** they contain no credentials, local runtime reports or private
  workspace names
