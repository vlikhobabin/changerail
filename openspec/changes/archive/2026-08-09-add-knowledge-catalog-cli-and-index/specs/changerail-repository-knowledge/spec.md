## ADDED Requirements

### Requirement: Repository maintenance CLI validation
ChangeRail MUST provide shared-runtime POSIX and native Windows helper
entrypoints for repository knowledge catalog validation.

#### Scenario: Maintainer validates default catalog and policy
- **WHEN** `bin/changerail-maintenance validate-catalog` runs without path overrides
- **THEN** the helper validates `.changerail/knowledge.yaml` and `.changerail/maintenance.yaml`
- **AND** exits zero only when schema and semantic validation pass

#### Scenario: Maintainer validates overridden paths
- **WHEN** `bin/changerail-maintenance validate-catalog --catalog <path> --policy <path>` runs
- **THEN** the helper validates the supplied repository-relative files
- **AND** rejects absolute or traversal override paths fail-closed

#### Scenario: Native Windows wrapper is available
- **WHEN** a native Windows operator invokes `bin\\changerail-maintenance.cmd`
- **THEN** the wrapper delegates to the same shared Python runtime command surface

### Requirement: Repository knowledge generated index
ChangeRail MUST render a deterministic repository knowledge index from validated
catalog and policy input, and MUST keep default and check mode read-only.

#### Scenario: Check mode observes no drift
- **WHEN** `bin/changerail-maintenance render-index --check` renders the expected index
- **AND** the configured generated index file already matches
- **THEN** the helper exits zero without modifying tracked files

#### Scenario: Check mode reports drift
- **WHEN** `bin/changerail-maintenance render-index --check` renders content that differs from the configured generated index file
- **THEN** the helper exits non-zero
- **AND** reports the configured generated index path
- **AND** does not modify the file

#### Scenario: Write mode updates only generated index
- **WHEN** `bin/changerail-maintenance render-index --write` runs
- **THEN** the helper writes only the configured generated index path
- **AND** repeated `--write` runs are idempotent

### Requirement: Repository knowledge index ordering
Repository knowledge index rendering MUST produce stable ordering independent of
YAML record order.

#### Scenario: Catalog order changes
- **WHEN** two valid catalogs contain the same records in different YAML order
- **THEN** rendered index content is identical

#### Scenario: Index lists catalog classifications
- **WHEN** the index is rendered
- **THEN** each catalog record appears with its path, status, type, owner and review metadata

### Requirement: Repository knowledge dogfood catalog
ChangeRail MUST include a minimal public-safe dogfood catalog for its canonical
docs and a generated index that can be checked by the maintenance CLI.

#### Scenario: Dogfood catalog validates
- **WHEN** `bin/changerail-maintenance validate-catalog` runs in the ChangeRail repository
- **THEN** the dogfood catalog and policy validate successfully

#### Scenario: Dogfood index is current
- **WHEN** `bin/changerail-maintenance render-index --check` runs in the ChangeRail repository
- **THEN** the generated dogfood index is current
