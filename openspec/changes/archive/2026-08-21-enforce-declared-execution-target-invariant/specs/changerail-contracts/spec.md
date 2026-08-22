## ADDED Requirements

### Requirement: Declared execution target contract
ChangeRail MUST принимать optional tracked `.changerail/execution-target.json`
только как `changerail.execution-target.v1` с bounded logical `id`,
non-sensitive `fingerprint` и `target_substitution_policy: forbid` и MUST
отклонять physical endpoint, credentials, target contents и unknown fields.

#### Scenario: Valid declaration принимается
- **WHEN** project содержит regular tracked declaration с точным v1 shape
- **THEN** ChangeRail получает canonical target identity projection
- **AND** не выполняет discovery, network access или provider commands

#### Scenario: Content-bearing declaration отклоняется
- **WHEN** declaration содержит endpoint, credential, environment value,
  arbitrary metadata или symlink/path escape
- **THEN** verification и delivery fail closed до child launch

### Requirement: Target-bound evidence contract
Если declaration присутствует, manifest, delivery status и runtime evidence MUST
ссылаться на один exact target id/fingerprint, а blocker и
evidence MUST NOT давать authority на provision, rebind или substitution.

#### Scenario: Evidence совпадает с declaration
- **WHEN** applicable runtime evidence содержит одну identity, совпадающую с
  captured declaration и manifest
- **THEN** target identity gate может пройти вместе с domain oracle checks

#### Scenario: Evidence не доказывает объявленную цель
- **WHEN** evidence отсутствует, ссылается на другую или несколько identities
- **THEN** review/publish gate fail closed
- **AND** raw endpoint или credential не запрашивается как remediation

### Requirement: Explicit target rebind invalidates prior lineage
Изменение tracked execution target MUST начинать новый clean delivery attempt и
MUST делать prior retained status, evidence, manifest и review verdict
неприменимыми.

#### Scenario: Declaration изменилась после blocker
- **WHEN** current target id/fingerprint не совпадает с retained identity
- **THEN** dirty resume fail closed до child launch
- **AND** оператор начинает новый clean attempt
