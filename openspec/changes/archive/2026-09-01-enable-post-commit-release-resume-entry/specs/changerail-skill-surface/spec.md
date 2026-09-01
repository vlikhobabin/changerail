## ADDED Requirements

### Requirement: Release publication entry routing is state-specific
`changerail-pub` и `changerail-deliver` MUST предоставлять явный
post-commit release resume entry, который выбирается до normal working-tree
review/scope gates и не расширяет external mutation authority.

#### Scenario: Maintainer starts initial release publication
- **WHEN** maintainer запускает `$changerail-pub <card>` без resume mode
- **THEN** publish MUST после final verification повторно выполнить
  deterministic preflight и current-worktree verdict validation с
  `--check-fresh` непосредственно перед первым staging
- **AND** publish MUST согласовать manifest с working tree до staging и со
  staged index после staging
- **AND** изменение bytes существующего same-path после раннего gate MUST
  остановить workflow до commit или push
- **AND** он MUST остановиться до commit или push при любом mismatch

#### Scenario: Maintainer resumes a pushed payload commit
- **WHEN** maintainer запускает `$changerail-pub <card> --resume-release`
- **THEN** publish MUST выбрать отдельный resume route до normal Review Gate
- **AND** route MUST NOT запускать current-worktree `--check-fresh`,
  working-tree/staged dirty-scope gates, staging или новый payload commit
- **AND** route MUST вместо них проверить positive verdict schema/result,
  clean card/workspace, payload parent/tree, committed manifest scope и exact
  remote feature-branch identity до release mutation
- **AND** route MUST отвергнуть replacement refs и graft state, а commit
  identity/parent/tree/diff/archive reads выполнять с replacement disabled

#### Scenario: Deliver routes a release resume
- **WHEN** maintainer запускает `$changerail-deliver <card> --resume-release`
- **THEN** deliver MUST детерминированно передать управление в тот же
  `changerail-pub` resume route
- **AND** deliver MUST NOT повторять `ff`, `do`, LLM review или normal publish
  freshness/scope entry для уже созданного payload commit

#### Scenario: Resume is requested from a pre-commit or dirty state
- **WHEN** resume route не может доказать clean `3.inprogress` card на exact
  payload commit и remote feature branch, равную этому commit
- **THEN** route MUST остановиться до любой mutation
- **AND** он MUST NOT использовать force, rebase, reset, stash, replacement
  objects, новый commit или дополнительный clean-HEAD LLM review для
  нормализации состояния

#### Scenario: Resume mode would broaden publication authority
- **WHEN** invocation требует новый provider, credential type, execution
  target, wire schema или mutation за пределами reviewed `1.0.0` transaction
- **THEN** lifecycle MUST остановиться как отдельный authorization или
  investigation scope
- **AND** `--resume-release` MUST NOT считаться источником такой authority
