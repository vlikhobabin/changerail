## ADDED Requirements

### Requirement: Решение для type-safe классификации decoded authorization target
ChangeRail MUST опубликовать tracked decision-only investigation до следующей
authorization implementation после двух последовательных отклоненных lineages
одного decoded-target defect class. Решение MUST сделать classification total
для любого JSON value, сохранить decoded object pairs, запретить hashing или
set membership непроверенных identity values, связать полную connected matrix и
выбрать ровно один новый exact authorization source.

#### Scenario: Decode сохраняет пары и не выпускает input exception
- **WHEN** exact field `Investigation authorization` содержит любой JSON value
- **THEN** parser декодирует ровно одно значение и представляет каждый object
  как ordered decoded key/value pairs, включая duplicate decoded keys
- **AND** trailing content, invalid JSON, top-level scalar/container values и
  произвольные nested values дают bounded classified result
- **AND** input-dependent `TypeError`, hash error, path error или иной Python
  exception не выходит без structured preflight result
- **AND** JSON вне exact source field не является authorization candidate

#### Scenario: Typed hints предшествуют target selection
- **WHEN** decoded candidates классифицируются для current successor и
  investigation dependency
- **THEN** parser линейно проверяет четыре identity keys в исходном pair order и
  создает hint только из validated non-empty string
- **AND** array, object, null, boolean и number identity values никогда не
  используются в hashing, set membership, mapping construction, path
  construction или semantic relation lookup
- **AND** current-target candidate имеет хотя бы один exact typed successor hint
  и хотя бы один exact typed investigation hint из trusted card/dependency
  metadata
- **AND** unrelated и fully distinct candidates не выбираются

#### Scenario: Candidate selection exact и fail closed
- **WHEN** все pair-preserved values получили typed target hints
- **THEN** до strict validation требуется ровно один current-target candidate
- **AND** ноль либо два и более matches возвращают authorization `invalid` с
  detail `authorization source must contain exactly one matching current target`
- **AND** canonical плюс malformed matching отклоняется как ambiguity, а
  canonical плюс unrelated или fully distinct сохраняет ровно один match
- **AND** единственный malformed matching candidate выбирается и отклоняется по
  earliest duplicate, shape или type rule, а не трактуется как unrelated

#### Scenario: Strict validation order предшествует semantics
- **WHEN** выбран ровно один current-target candidate
- **THEN** validation по порядку проверяет duplicate decoded keys, exact
  six-field shape, identity string types, integer-not-boolean ceiling range,
  protocol boolean type и exact typed target equality
- **AND** parser материализует mapping только после уникальности keys и valid
  types всех required values
- **AND** filesystem, published/tracked card и reciprocal relation semantics
  запускаются только над validated mapping
- **AND** review eligibility вычисляется только после прохождения всех semantic
  checks

#### Scenario: Structural rejection имеет единый machine oracle
- **WHEN** decode, selection, duplicate, shape, identity type, range, boolean
  либо typed-target validation завершается отказом
- **THEN** preflight возвращает exit 1, outcome `investigation-required`,
  authorization status `invalid`, exact row detail, `llm_review.required` false
  и reason `complexity guard requires investigation/simplification`
- **AND** `semantic_check_delta`, `semantic_review_dispatch_delta` и
  `model_launch_delta` равны нулю
- **AND** `uncaught_exception` равен false
- **AND** semantic relation failures могут иметь `semantic_check_delta` один,
  но сохраняют `semantic_review_dispatch_delta` и `model_launch_delta` нулевыми
  и не получают review eligibility

#### Scenario: Identity matrix покрывает каждый key, value kind и duplicate order
- **WHEN** будущий authorization parser готовится к review
- **THEN** каждый из `investigation_card`, `investigation_id`, `successor_card` и
  `successor_id` имеет connected single-value rows для exact string, empty
  string, distinct string, null, true, false, integer, float, array и object
- **AND** каждый key имеет positives с legal equivalent escaped key/value
- **AND** каждый key пересекается с каждым перечисленным value в обоих orders:
  literal-then-alternate-escaped и alternate-escaped-then-literal duplicate
- **AND** каждый duplicate row возвращает exact detail `authorization source
  contains duplicate decoded key: <key>` до type, schema либо semantic dispatch
  независимо от duplicate values

#### Scenario: Connected matrix покрывает shape и candidate cardinality
- **WHEN** запускается full focused matrix
- **THEN** она покрывает каждый missing required field, extra fields, каждый
  top-level JSON kind, ceiling boundaries/types и protocol allowance types
- **AND** она покрывает canonical, unrelated, distinct и malformed candidates в
  zero-, one- и multiple-match combinations, а также JSON вне exact field
- **AND** она покрывает source, successor и investigation path/id/status/tracked
  state и reciprocal relation mutations
- **AND** каждый mutated fixture сначала доказывает passing fresh unmodified
  canonical base на той же production preflight boundary и записывает exact
  structured actual/expected results и owned dispatch counters

#### Scenario: Выбран один replacement authorization source
- **WHEN** эта investigation опубликована и разрешена follow-up work
- **THEN** единственный следующий work item —
  `authorize-type-safe-phase-routed-resume-integrity-payload` с initial path
  `openspec/board/2.todo/authorize-type-safe-phase-routed-resume-integrity-payload.md`
  и published path
  `openspec/board/4.done/authorize-type-safe-phase-routed-resume-integrity-payload.md`
- **AND** он зависит от
  `investigate-type-safe-decoded-target-classification-boundary`, блокирует
  `replace-phase-routed-resume-integrity-boundary`, меняет только owning parser
  и connected smoke production surface и остается в пределах 300 added
  production LOC
- **AND** rejected source/rescue payloads остаются forensic-only без repair,
  publication или reuse как новый tracked source

#### Scenario: Exact object сохраняет bounded downstream authority
- **WHEN** новый authorization source позднее опубликован
- **THEN** он содержит ровно один object, связывающий published investigation
  `investigate-type-safe-decoded-target-classification-boundary` с successor
  `replace-phase-routed-resume-integrity-boundary` по exact `3.inprogress` path,
  production LOC ceiling 500 и `allow_new_authority_or_wire_protocol` true
- **AND** successor ссылается только на published source
  `authorize-type-safe-phase-routed-resume-integrity-payload` по exact `4.done`
  path и id
- **AND** измерение successor 501 или больше останавливает работу для новой
  investigation и split authorization вместо повышения ceiling

#### Scenario: Review handoff не circular
- **WHEN** эта investigation или будущий authorization item завершает
  implementation/verification handoff
- **THEN** fresh independent review запускается для получения `GO` или `NO-GO`
  без требования GO на входе
- **AND** только fresh GO разрешает publish и deterministic finalization
- **AND** этот decision-only change не создает authorization card или
  implementation successor

#### Scenario: Fast-forward остается planning-only
- **WHEN** `$changerail-ff` завершает эту investigation
- **THEN** создаются или обновляются только ее board card и один active OpenSpec
  change
- **AND** production code, schemas, tests, CLI, synced main specs, public runtime
  docs и runtime behavior остаются без изменений
