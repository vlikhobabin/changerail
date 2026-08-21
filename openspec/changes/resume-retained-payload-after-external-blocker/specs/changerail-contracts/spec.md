## ADDED Requirements

### Requirement: Recoverable external blocker contract
`changerail.delivery-run.v1` MUST разрешать bounded объект
`changerail.external-blocker.v1` только для blocked attempt. Объект MUST
содержать run-local blocker id, known class, observation timestamp,
`retryable: true` и bounded required evidence ids/maximum age, а также MUST
отклонять prompts, values, response bodies, screenshots и raw output.

#### Scenario: Value-free blocker проходит валидацию
- **WHEN** blocked run записывает known class и normalized evidence ids без
  content-bearing fields
- **THEN** delivery-run schema validation проходит
- **AND** последующий resume может проверить policy без parsing terminal prose

#### Scenario: Secret-bearing blocker не проходит валидацию
- **WHEN** blocker metadata включает entered credential, environment value,
  response body, screen content или arbitrary project-specific reason
- **THEN** schema validation fail closed
- **AND** record не может разрешить retained resume

### Requirement: External resume evidence contract
Retained external resume MUST ссылаться на schema-valid ignored evidence index,
scope которого идентифицирует source run/card, а required entries имеют passed,
fresh и redacted state согласно blocker policy.

#### Scenario: Fresh evidence принимается
- **WHEN** каждый required evidence id существует один раз, имеет
  `status: passed`, принадлежит source scope и завершен после blocker observation
  в пределах maximum age
- **THEN** resume записывает fresh passing checks для blocker, evidence и
  payload identity
- **AND** raw evidence output не копируется в delivery status

#### Scenario: Evidence нельзя переиспользовать между scope
- **WHEN** evidence принадлежит другому card/run, не содержит required id,
  является stale или сообщает non-passing status
- **THEN** resume status становится `BLOCKED` со stable failure reason
- **AND** child continuation не запускается

### Requirement: Aggregate retained external recovery contract
`changerail.delivery-plan-status.v1` MUST представлять source run/status, card,
fingerprint, blocker id/class и evidence policy для resume одного original
child, не изменяя существующий investigation recovery object.

#### Scenario: Plan status сохраняет resumable context
- **WHEN** child завершается на valid recoverable external blocker
- **THEN** aggregate card status сохраняет bounded recovery context и source
  identity
- **AND** raw logs и evidence contents остаются indirect ignored references

### Requirement: Retained recovery SHALL preserve declared execution target
Если project contract объявляет execution target, delivery-run и plan-status MUST
сохранять его logical id/fingerprint в retained identity и MUST NOT
принимать blocker/evidence как authority на provision, rebind или substitution.

#### Scenario: Target identity совпадает
- **WHEN** blocker, current project declaration и target-bearing recovery
  evidence ссылаются на тот же logical id/fingerprint
- **THEN** target identity check может пройти вместе с остальными resume gates
- **AND** physical endpoint и credentials не копируются в status.

#### Scenario: Target identity изменилась
- **WHEN** current declaration отсутствует, имеет другой fingerprint или
  evidence относится к другой/нескольким целям
- **THEN** retained resume fail closed
- **AND** explicit rebind требует нового clean delivery attempt.
