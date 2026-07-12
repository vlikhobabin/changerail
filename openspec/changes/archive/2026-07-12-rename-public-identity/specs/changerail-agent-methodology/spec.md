## ADDED Requirements

### Requirement: ChangeRail public methodology identity
The reusable agent methodology MUST use ChangeRail as the canonical product
name and MUST describe OpenSpec as the artifact/spec workflow dependency rather
than as the product identity.

#### Scenario: Consumer reads shared methodology
- **WHEN** a consumer project receives generated agent methodology
- **THEN** the methodology identifies ChangeRail as the workflow/toolchain
  layer
- **AND** it identifies OpenSpec as the artifact/spec workflow dependency

#### Scenario: Public examples are reviewed
- **WHEN** tracked methodology examples are reviewed before commit
- **THEN** canonical source-of-truth examples use `/opt/changerail`
- **AND** old `/opt/opsx` examples appear only in explicit migration or history
  notes
