## ADDED Requirements

### Requirement: Repository knowledge contract schemas
ChangeRail MUST provide tracked JSON schemas for repository knowledge catalog and
maintenance policy contracts using canonical `changerail.*` schema ids.

#### Scenario: Maintainer inspects repository knowledge schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.repository-knowledge.v1` and `changerail.maintenance-policy.v1`

#### Scenario: Contract schema smoke covers repository knowledge schemas
- **WHEN** `python3 scripts/smoke-contract-schemas.py` runs
- **THEN** the smoke validates representative valid and invalid documents for both schema ids
