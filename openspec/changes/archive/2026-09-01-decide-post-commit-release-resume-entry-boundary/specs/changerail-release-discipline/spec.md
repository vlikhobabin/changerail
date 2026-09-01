## ADDED Requirements

### Requirement: First stable post-commit resume boundary investigation decision
ChangeRail MUST опубликовать отдельное decision-only investigation перед
bounded authorization exact successor, который устраняет недостижимый
post-commit publication resume entry первого stable release.

#### Scenario: Final review blocker is classified before replacement delivery
- **WHEN** final predecessor review установил, что normal current-worktree
  freshness и dirty scope gates безусловно выполняются для clean payload commit
- **THEN** investigation MUST зафиксировать state-specific normal/resume entry
  boundary и committed lineage/scope/remote proofs
- **AND** оно MUST сохранить normal pre-staging gates и существующую exact
  release identity machine
- **AND** оно MUST NOT реализовывать successor, создавать release objects,
  менять schemas/source classification или выдавать inline/free-form waiver

#### Scenario: Exact successor requires a separate bounded authorization
- **WHEN** measured predecessor baseline равен 299 added production-counted LOC
  и минимальный successor forecast равен 359..399
- **THEN** hard successor ceiling MUST быть 400 cumulative added
  production-counted LOC
- **AND** отдельный published authorization MUST связать investigation
  `investigate-post-commit-release-resume-entry-boundary` с exact successor
  `enable-post-commit-release-resume-entry`
- **AND** authorization MUST объявить `production_loc_ceiling: 400` и
  `allow_new_authority_or_wire_protocol: false`
- **AND** authorization-card MUST объявить
  `investigate-post-commit-release-resume-entry-boundary` в `Depends On`
- **AND** exact successor MUST объявить тот же investigation id в `Depends On`
  в дополнение к two-field published authorization reference
- **AND** canonical deterministic preflight MUST проверить обе dependency edges
  и fail closed при missing или mismatched relation
- **AND** measurement 401 или больше MUST остановить successor для split или
  нового investigation без ослабления classification или regression floor

#### Scenario: Successor implementation boundary remains minimal and observable
- **WHEN** exact successor получает matching clean published authorization
- **THEN** implementation MUST ограничиться early pub/deliver routing,
  read-only committed target существующего manifest helper, focused committed
  scope и wiring probes, существующими specs и release docs
- **AND** implementation MUST NOT добавлять workflow, provider, credential
  type, execution target, wire schema или новую mutation authority
- **AND** focused probes MUST наблюдать разные normal/resume gate sets и
  fail-closed wrong lineage, scope, card, remote и release identity outcomes

#### Scenario: Exact successor reaches final review
- **WHEN** bounded successor готов к independent review
- **THEN** deterministic preflight MUST принять exact published authorization,
  cumulative LOC не выше 400 и единый manifest всего successor payload
- **AND** на одном exact tree MUST последовательно пройти core, extended и
  release-CI suites, public/history scans, dependency integrity, reproducible
  distribution и strict config/OpenSpec/diff checks
- **AND** fresh-context xhigh review MUST проверить тот же exact tree до любой
  publication mutation
