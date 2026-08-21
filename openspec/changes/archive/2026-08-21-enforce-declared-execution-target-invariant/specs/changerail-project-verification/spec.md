## ADDED Requirements

### Requirement: Project verification MUST validate declared target safely
`verify-project` MUST schema-validate regular tracked execution-target
declaration и MUST fail closed на unsafe path, invalid shape или content-bearing
fields без выполнения project/provider commands.

#### Scenario: Declaration schema valid
- **WHEN** optional declaration имеет exact v1 shape
- **THEN** verification сообщает target identity contract pass без вывода
  sensitive values

#### Scenario: Declaration invalid or unsafe
- **WHEN** declaration является symlink, содержит unknown fields либо не
  проходит schema
- **THEN** verification сообщает bounded failure и не запускает delivery
