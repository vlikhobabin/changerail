## ADDED Requirements

### Requirement: ChangeRail maintenance dogfood scope
ChangeRail MUST configure an explicit public-safe dogfood maintenance scope for
canonical ChangeRail knowledge files and MUST enable applicable deterministic
built-in detectors for that scope.

#### Scenario: Dogfood scan has detector coverage
- **WHEN** `bin/changerail-maintenance scan --json` runs in the ChangeRail repository
- **THEN** the scan report is complete and schema-valid
- **AND** it includes non-zero deterministic detector coverage for the configured dogfood scope
- **AND** tracked repository files are not modified

#### Scenario: Dogfood catalog and index stay current
- **WHEN** `bin/changerail-maintenance validate-catalog` and `bin/changerail-maintenance render-index --check` run in the ChangeRail repository
- **THEN** the dogfood catalog and generated index validate successfully

### Requirement: Repository knowledge deterministic fixtures
ChangeRail MUST include public-safe fixtures for deterministic maintenance
detector boundaries and stable failure codes.

#### Scenario: Broken link fixture fails with stable codes
- **WHEN** the repository knowledge smoke test runs the broken link and anchor fixture
- **THEN** missing-target and stale-anchor findings are reported with stable detector and rule ids

#### Scenario: Stale generated index fixture fails with stable code
- **WHEN** the repository knowledge smoke test runs the stale generated index fixture
- **THEN** a stale-generated-output finding is reported with a stable detector and rule id
- **AND** the fixture generated file is not rewritten by check mode

#### Scenario: Optional instruction producer fixture remains unknown
- **WHEN** quality rollup runs without a published card `050` instruction-budget producer record
- **THEN** instruction byte metrics are reported as `unknown`
- **AND** ChangeRail does not invent a temporary threshold or producer schema

### Requirement: Maintenance contradiction annotation boundary
ChangeRail MUST keep semantic contradiction evidence as agent annotation or
proposal evidence and MUST NOT treat a single model verdict as a deterministic
maintenance scan failure.

#### Scenario: Contradiction annotation is retained as evidence
- **WHEN** an agent supplies schema-valid contradiction annotation evidence to maintenance quality inputs
- **THEN** ChangeRail can report the annotation as quality evidence
- **AND** deterministic scan does not fail solely because of one model verdict

#### Scenario: Deterministic scan ignores model-only contradiction
- **WHEN** the repository contains only model-authored contradiction annotation evidence without a deterministic detector finding
- **THEN** `bin/changerail-maintenance scan --json` does not classify that annotation as a deterministic gate failure

### Requirement: Maintenance dogfood public safety
ChangeRail dogfood maintenance fixtures and configuration MUST remain
public-safe and default to read-only operation.

#### Scenario: Dogfood runtime output is ignored
- **WHEN** dogfood scan, report or quality commands retain runtime output
- **THEN** the output remains below ignored `.runtime/changerail/maintenance/`
- **AND** tracked files contain only public-safe configuration, fixtures, schemas and docs

#### Scenario: Feedback adapters are not default CI dependency
- **WHEN** default repository knowledge smoke tests run in a clean repository
- **THEN** feedback and runtime-dependent adapters are exercised by fixtures only
- **AND** the tests do not require pre-existing ignored local review or delivery history
