## MODIFIED Requirements

### Requirement: Placeholder contract
Project templates MUST separate portable tracked scope placeholders from
machine-local absolute path placeholders.

#### Scenario: Bootstrap renders portable project-local files
- **WHEN** bootstrap renders templates in the default config mode
- **THEN** generated tracked files avoid raw absolute consumer project paths
- **AND** project-local config still scopes filesystem access to the generated
  repository

### Requirement: Public-safe template content
Project templates MUST avoid machine-local absolute consumer paths in default
tracked output.

#### Scenario: Public-surface scan covers portable generated templates
- **WHEN** templates are rendered in default mode and scanned before commit
- **THEN** generated tracked files contain no private username, customer name
  or machine-local absolute path
