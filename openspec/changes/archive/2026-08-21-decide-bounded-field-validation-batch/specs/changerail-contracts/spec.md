## ADDED Requirements

### Requirement: Field-validation successors MUST use bounded investigation decisions
ChangeRail MUST require bounded decisions for exact successors
`enforce-declared-execution-target-invariant`,
`expose-structured-live-delivery-progress`,
`resume-retained-payload-after-external-blocker`,
`report-recovery-aware-delivery-episodes`,
`define-verification-coverage-map` и
`materialize-versioned-source-classification-profiles`, которые получают отдельные
published authorization sources с ceiling не выше 500 и protocol allowance
только после tracked investigation decision, которая перечисляет их в Blocks.

#### Scenario: Exact successor использует bounded source
- **WHEN** successor ссылается на отдельный `4.done` authorization source,
  bound к этому investigation и exact `3.inprogress` card path
- **THEN** deterministic preflight может применить ceiling до 500 и accepted
  protocol allowance

#### Scenario: Payload расширяет decision
- **WHEN** production LOC выше 500, successor/path не совпадает, появляется
  новая authority boundary или повторяется unresolved blocker hypothesis
- **THEN** authorization неприменима
- **AND** delivery требует split или новую investigation

### Requirement: Repeated field defect MUST become one bounded hypothesis
Investigation MUST разрешать post-investigation successor снять repeated-defect
stop только когда decision фиксирует single-source implementation boundary,
verification floor и отсутствие дополнительного same-card rescue budget.

#### Scenario: Bounded successor реализует decision
- **WHEN** successor сохраняет exact investigated scope и dependency lineage
- **THEN** card может объявить `Repeated defect class: no`
- **AND** protocol/LOC authorization остается обязательной

#### Scenario: Тот же defect повторяется после bounded implementation
- **WHEN** verification или review снова обнаруживает тот же unresolved
  invariant/blocker class
- **THEN** successor не расширяет scope под текущей authorization
- **AND** создается linked investigation или split decision
