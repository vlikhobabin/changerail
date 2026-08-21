## ADDED Requirements

### Requirement: Templates SHALL expose optional execution target declaration
Project templates SHALL документировать schema-valid optional
`.changerail/execution-target.json` без platform-specific defaults, endpoint,
credentials или generated target identity.

#### Scenario: Project adopts target binding
- **WHEN** maintainer добавляет declaration из generic template/example
- **THEN** файл содержит только logical id, fingerprint и forbid policy
- **AND** project-owned process отвечает за значения и oracle evidence

#### Scenario: Project does not need target binding
- **WHEN** declaration не добавлена
- **THEN** bootstrap и verification сохраняют legacy-compatible behavior
