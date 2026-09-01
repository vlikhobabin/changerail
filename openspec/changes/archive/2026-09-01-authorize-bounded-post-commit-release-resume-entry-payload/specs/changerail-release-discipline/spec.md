## ADDED Requirements

### Requirement: First stable bounded post-commit resume authorization source
ChangeRail MUST опубликовать отдельную clean tracked authorization-card,
которая связывает published first-stable post-commit resume investigation
только с exact successor и задаёт bounded cumulative production LOC ceiling
без новой authority или wire protocol.

#### Scenario: Authorization source publishes the exact bounded object
- **WHEN** authorization-card
  `authorize-bounded-post-commit-release-resume-entry-payload` проходит
  собственные delivery, independent review и publish
- **THEN** card в
  `openspec/board/4.done/authorize-bounded-post-commit-release-resume-entry-payload.md`
  MUST содержать ровно один machine-readable authorization object и ровно
  шесть полей без дополнительных ключей
- **AND** `investigation_card` MUST быть равен
  `openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md`
- **AND** `investigation_id` MUST быть равен
  `investigate-post-commit-release-resume-entry-boundary`
- **AND** `successor_card` MUST быть равен
  `openspec/board/3.inprogress/enable-post-commit-release-resume-entry.md`
- **AND** `successor_id` MUST быть равен
  `enable-post-commit-release-resume-entry`
- **AND** `production_loc_ceiling` MUST быть integer `400`
- **AND** `allow_new_authority_or_wire_protocol` MUST быть boolean `false`
- **AND** authorization-card MUST объявить
  `investigate-post-commit-release-resume-entry-boundary` в `Depends On`

#### Scenario: Deterministic preflight consumes only the exact reciprocal chain
- **WHEN** canonical deterministic preflight оценивает published
  authorization reference exact successor
- **THEN** successor MUST существовать только по path
  `openspec/board/3.inprogress/enable-post-commit-release-resume-entry.md` с id
  `enable-post-commit-release-resume-entry`
- **AND** successor MUST объявить
  `investigate-post-commit-release-resume-entry-boundary` в `Depends On` и
  exact two-field reference на published authorization-card
- **AND** preflight MUST проверить investigation dependency и в
  authorization-card, и в successor вместе с exact six-field object и exact
  successor identity/path
- **AND** missing, unpublished, duplicated, extra или mismatched field,
  identity, path, dependency или reference MUST вернуть fail-closed
  `investigation-required` до semantic review
- **AND** authorization MUST NOT применяться к другой card как
  переиспользуемый waiver

#### Scenario: Successor stays inside both planned and hard LOC boundaries
- **WHEN** deterministic review preflight измеряет cumulative exact successor
  payload относительно measured predecessor baseline `299`
- **THEN** investigated forecast MUST оставаться `359..399`, а planned
  increment MUST быть не больше `100` production-counted строк
- **AND** machine-readable authorization hard ceiling MUST оставаться `400`
- **AND** измерение `401` или больше MUST fail closed и потребовать split или
  нового investigation без изменения source classification или ослабления
  regression floor
- **AND** ceiling MUST NOT разрешать новую schema, provider, credential,
  workflow, mutation authority или wire protocol

#### Scenario: Authorization delivery remains docs and OpenSpec only
- **WHEN** maintainer доставляет authorization-card до её публикации
- **THEN** payload MUST быть ограничен card, OpenSpec delta, spec sync и archive
  metadata
- **AND** exact successor card и её authorization reference MUST оставаться
  неизменными до публикации authorization-card
- **AND** production/runtime/test implementation, release-card, tag, GitHub
  Release, assets и release mutation MUST отсутствовать
