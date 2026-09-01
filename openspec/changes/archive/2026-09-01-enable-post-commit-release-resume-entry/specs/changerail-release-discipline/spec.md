## ADDED Requirements

### Requirement: First stable publication resume is bound to committed lineage
Post-commit возобновление публикации ChangeRail `1.0.0` MUST принимать только
существующий clean payload commit, однозначно связанный с positive successor
verdict, единым delivery manifest и authorized remote feature branch.

#### Scenario: Pushed reviewed payload enters resume
- **WHEN** resume mode получает существующие verdict и manifest для successor
  release card
- **THEN** verdict MUST пройти validation существующей schema и иметь
  `result: go` без current-worktree freshness claim
- **AND** parent payload commit MUST равняться
  `verdict.workspace.head_commit`
- **AND** payload commit tree MUST равняться `verdict.workspace.tree_sha`
- **AND** workspace MUST быть чистым, а exact card MUST оставаться в
  post-commit `3.inprogress`
- **AND** committed `parent..payload` diff MUST в точности совпадать с
  manifest committable scope
- **AND** local replacement refs и graft state MUST отсутствовать, а commit
  identity/parent/tree/diff/archive reads MUST использовать raw-object
  semantics с replacement processing disabled
- **AND** authorized remote feature branch MUST указывать ровно на payload
  commit до tag/release/assets mutation

#### Scenario: Resume lineage or scope cannot be proved
- **WHEN** verdict отсутствует, invalid или negative, lineage неполна, commit
  имеет unexpected parent/tree, workspace/card dirty или wrong-state,
  replacement/graft state присутствует, manifest scope отличается либо remote
  branch указывает на другой commit
- **THEN** publication MUST fail closed до mutation
- **AND** workflow MUST NOT исправлять состояние через новый review/commit,
  force, rebase, reset, stash или расширение authority

### Requirement: First stable publication resumes from the first absent exact step
После успешного committed-lineage admission release continuation MUST заново
доказать полную external identity и продолжить только с первого отсутствующего
шага существующей `v1.0.0` transaction.

#### Scenario: Transaction was interrupted after a safe handoff
- **WHEN** prior invocation остановилась после payload push, tag creation,
  hosted release creation или partial contracted asset upload
- **THEN** resume MUST read-only проверить все уже присутствующие объекты
- **AND** exact matching steps MUST быть приняты idempotently
- **AND** workflow MUST продолжить с первого доказанно отсутствующего шага
  без повторного payload commit или clean-HEAD LLM review

#### Scenario: Existing release identity is exact
- **WHEN** existing tag/release/assets проверяются для resume
- **THEN** annotated `v1.0.0` MUST указывать на payload commit и иметь exact
  annotation `ChangeRail 1.0.0`
- **AND** public non-draft non-prerelease release MUST иметь exact title
  `ChangeRail 1.0.0` и полный notes body из tracked
  `docs/releases/1.0.0.md`
- **AND** каждый present asset MUST иметь уникальный contracted basename и
  byte-match с fresh build из dereferenced tag
- **AND** загружаться MUST только доказанно отсутствующие contracted basenames

#### Scenario: Existing release identity is wrong or unprovable
- **WHEN** tag target/type/annotation, release tag/title/notes/state или asset
  basename/uniqueness/bytes отличаются либо требуемое evidence отсутствует
- **THEN** resume MUST остановиться без mutation
- **AND** tag, release или asset MUST NOT быть force-updated, replaced или
  принят по неполному identity proof

#### Scenario: Initial publication remains a pre-staging certification gate
- **WHEN** successor release впервые переходит от reviewed working tree к
  payload commit
- **THEN** весь original release qualification floor MUST пройти на одном
  exact successor tree, сначала core и затем extended
- **AND** fresh independent xhigh final review MUST вернуть `GO` для того же
  tree до любой publication mutation
- **AND** initial publish MUST сохранить deterministic preflight,
  current-worktree freshness и working-tree/staged scope checks
- **AND** после final verification initial publish MUST повторить preflight,
  `--check-fresh` и working-tree scope непосредственно перед staging и
  остановиться до commit/push при intervening same-path byte mutation
