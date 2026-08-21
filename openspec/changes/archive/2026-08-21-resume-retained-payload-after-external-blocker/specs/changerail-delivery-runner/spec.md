## ADDED Requirements

### Requirement: Recoverable external blocker stop
Delivery runner MUST считать temporary external blocker recoverable только
когда authoritative structured child event объявляет known blocker class,
bounded resume-evidence requirements и canonical retained-payload identity.

#### Scenario: Required external gate временно недоступен
- **WHEN** delivery child сообщает `BLOCKED` со schema-valid recoverable
  external blocker на mandatory platform, service, credential, license или
  required-software gate
- **THEN** runner записывает bounded blocker и exact retained identity
- **AND** не сообщает delivery success и не обходит последующий review

#### Scenario: Free-text blocker не является authoritative
- **WHEN** child prose или stderr описывает external blocker без structured
  contract либо называет unknown/nonrecoverable class
- **THEN** runner оставляет attempt blocked и non-resumable
- **AND** не разрешает dirty workspace на основании этого текста

### Requirement: Evidence-bound retained external resume
Single-card resume MUST запускать child с dirty workspace только когда prior
status identity, blocker class, exact retained fingerprint и все declared fresh
recovery evidence проходят валидацию. Evidence доказывает только retry
eligibility; resumed lifecycle MUST повторить mandatory verification и
review/publish gates.

#### Scenario: External condition восстановлен
- **WHEN** оператор передает schema-valid evidence index в scope source run/card
  со всеми required passed entries новее blocker
- **AND** current workspace и retained fingerprint точно совпадают с prior
  status
- **THEN** resume запускает original card с value-free recovery context
- **AND** resumed child повторяет mandatory external gate до возможного delivery
  success

#### Scenario: Resume input stale или mismatched
- **WHEN** evidence отсутствует, stale, failed, относится к другому run/card
  либо payload/workspace identity drifted
- **OR** target-bound recovery evidence has missing, mismatched or multiple
  entry target identities
- **THEN** resume завершается non-zero до Codex launch
- **AND** status записывает stable machine-classified blocker reason

### Requirement: Queue parity for recoverable external blocker
`resume-plan` MUST валидировать и возобновлять original externally blocked child
до продолжения dependency queue, сохраняя completed cards и workspace
serialization.

#### Scenario: Original child успешно возобновляется
- **WHEN** aggregate plan содержит одну valid retained external recovery и
  supplied evidence проходит
- **THEN** `resume-plan` сначала запускает эту карточку, а затем освобождает ее
  downstream dependencies после normal delivery success
- **AND** уже delivered prior plan карточки остаются skipped

#### Scenario: Duplicate или mixed recovery отклоняется
- **WHEN** plan state объявляет несколько recovery paths для одной source card
  либо recovery identity принадлежит другому workspace/card
- **THEN** queue resume fail closed до запуска child
- **AND** downstream cards остаются explicitly blocked

### Requirement: External recovery SHALL NOT substitute a declared target
Runner MUST сохранять exact declared execution target across retained resume и
MUST завершаться до Codex launch при target drift или попытке использовать
recovery как authority на создание, переподключение или подмену среды.

#### Scenario: Recovery evidence указывает другую цель
- **WHEN** evidence target id/fingerprint или target-bound entry
  id/fingerprint не совпадает с source retained identity
- **THEN** single-card и queue resume fail closed со stable target-mismatch
  reason
- **AND** child не запускается и downstream queue не освобождается.

#### Scenario: Оператор явно переподключил среду
- **WHEN** tracked project target identity изменилась после blocked attempt
- **THEN** dirty retained resume недоступен
- **AND** оператор начинает новый clean delivery attempt с новой verification
  lineage.
