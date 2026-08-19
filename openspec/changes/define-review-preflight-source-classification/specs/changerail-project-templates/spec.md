## ADDED Requirements

### Requirement: Consumer templates document source classification
Project templates MUST document the optional
`.changerail/source-classification.yaml` review-preflight source classification
file as project-owned tracked configuration. Generated defaults MUST remain
public-safe and MUST NOT declare domain-specific production roots unless the
operator explicitly opts in.

#### Scenario: Consumer guidance is generated
- **WHEN** bootstrap renders a generic consumer project
- **THEN** generated guidance explains that domain-specific production source
  kinds can be declared in `.changerail/source-classification.yaml`
- **AND** the generated content does not hard-code application-specific source
  roots or real customer data

#### Scenario: Consumer does not opt in
- **WHEN** a generated consumer has no source-classification file
- **THEN** review preflight uses the built-in generic classifier
- **AND** bootstrap does not create a false production declaration on behalf of
  the project
