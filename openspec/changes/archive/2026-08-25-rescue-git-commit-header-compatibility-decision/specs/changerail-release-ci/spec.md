## ADDED Requirements

### Requirement: Git-compatible commit headers MUST иметь bounded semantic tree boundary
ChangeRail MUST считать exhausted
`deliver-structurally-bounded-public-history-scan` payload и его evidence
forensic-only и MUST определять raw commit parser clean replacement через
одну exact bounded grammar. Batch-validated commit body MUST быть не
больше `64 MiB`, header block MUST быть не больше `64 MiB - 2` bytes
и содержать не больше `1,000,000` physical lines. Первая physical line
MUST точно равняться `tree SP` плюс 40 lowercase hexadecimal bytes.
Каждая later initial line MUST содержать `1..255` byte key из printable
non-space ASCII, required first `SP` и opaque possibly-empty value без NUL,
ASCII control или DEL. Continuation MUST начинаться с `SP`, MAY быть
exact `b" "` и MUST следовать за later non-`tree` logical header. Только
first tree OID MUST интерпретироваться; все later headers, включая
parent, identity, signature, mergetag и unknown keys, MUST оставаться opaque.

#### Scenario: Pinned source ancestry и planning snapshot моделируются read-only
- **WHEN** maintainers применяют minimal parser model к exact source ancestry
  `git rev-list 644e9e1bf03fa444d603652b17d7262846149978` и separately pinned
  planning `git rev-list --all` snapshot
- **THEN** source ancestry имеет `95/95` accepted/rejected `0`, ordered
  `sha256:8576a6f652fa2d168d0956ff225471c92b5190fc46cef707bdae2472584b86ba`
  и sorted
  `sha256:0771d6bc5ad5f121ac630d58805eba30185e84f53595c6ec117f5138ca597eb7`
- **AND** planning snapshot имеет `98/98` accepted/rejected `0`, extra-ref
  OIDs `e0ec75135e8a35be5283a9d6de556dc63f43e260`,
  `e2a39bec92a165a63ede6e3835dc03807fd6ff8f` и
  `e7f5542d91aad1c79545f6a2239f87d3761e9180`, ordered
  `sha256:31c8ae5d7a32a748e5efd371c63d2ae622949d1c8c7c8241c730dd3678c0460e`,
  sorted `sha256:f0545cd40fb856e5153821988a9156941c519c8738abdc11088362b0f58c425d`
  и sorted ref snapshot
  `sha256:5b53eac521b1d0618949bbbc2b89b86c5adb4b208c307ca53bd78baac180fad5`
- **AND** каждая population содержит три signed commits, 48 continuation lines и
  шесть exact blank folds, а commit
  `4fb01e7a12c43ab5c5ff06b1388743433846b54d` остаётся named regression
  без превращения raw objects и forensic runtime output в tracked authority

#### Scenario: Traversal получает ровно один semantic tree
- **WHEN** raw commit начинается с exact `tree <40 lowercase hex>`, имеет
  bounded header block и только valid later opaque logical headers
- **THEN** traversal получает только этот first tree OID
- **AND** `parent`, `author`, `committer`, `gpgsig`, `mergetag`, `encoding` и
  unknown later values не whitelist, не декодируются и не используются

#### Scenario: Blank и unknown folds valid
- **WHEN** later unknown, signature или mergetag logical header имеет один или
  несколько `SP`-prefixed continuations, включая exact physical line `b" "`
- **THEN** commit framing остаётся valid, а каждый continuation остаётся opaque
- **AND** empty initial value, additional leading value spaces и non-ASCII
  value bytes valid, если не содержат NUL, ASCII control или DEL

#### Scenario: Commit header framing malformed
- **WHEN** tree missing, late, duplicated, continued, uppercase, short, long или
  non-hex; continuation не имеет preceding non-tree logical header; required
  first `SP` или `LF LF` отсутствует; tab/control/DEL/non-ASCII byte находится
  до first `SP`; value нарушает byte class; либо body, header, key или
  physical-line count превышает exact bound
- **THEN** history scanning fails closed до traversal tuples, cache reuse, partial
  findings или successful text/JSON output
- **AND** arbitrary message bytes после first `LF LF` не считаются commit headers,
  а further `SP` после first `SP` является opaque value

#### Scenario: Replacement tests проверяют raw objects и все bounds
- **WHEN** future replacement проверяет commit-header parser
- **THEN** он создаёт real raw commit objects для blank и unknown folded
  headers и проверяет key lengths `1/255/256`, injected-small exact/one-over
  body/header/line bounds, missing first `SP`, bad key bytes, orphan continuation и
  every malformed tree/value/fold transition
- **AND** он сохраняет full batch framing, fault injection, exact child count,
  independent tuples, legacy parity, no-partial-output и byte-identical
  refs/worktree/index no-mutation matrix

#### Scenario: Clean authorization и replacement выполняются по порядку
- **WHEN** maintainers продолжают после independent review и publication этого
  rescue investigation
- **THEN** они сначала создают и публикуют
  `authorize-bounded-git-commit-header-compatible-history-scan` с exact object
  `{"investigation_card":"openspec/board/4.done/rescue-git-commit-header-compatibility-decision.md","investigation_id":"rescue-git-commit-header-compatibility-decision","successor_card":"openspec/board/3.inprogress/deliver-git-compatible-structural-public-history-scan-replacement.md","successor_id":"deliver-git-compatible-structural-public-history-scan-replacement","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`
- **AND** только после remote reachability clean tracked source можно создать
  exact replacement с единственной reference
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-git-commit-header-compatible-history-scan.md","authorization_id":"authorize-bounded-git-commit-header-compatible-history-scan"}`

#### Scenario: Replacement scope или review contract drift
- **WHEN** replacement не использует exact reciprocal ids/paths, начинается
  до publication clean authorization, превышает 300 added production LOC
  относительно `ccccb62562e1646b595119edd3326763860f14a7`, объявляет новый
  authority/protocol, не использует `critical`/`xhigh` repeated-defect
  review или даёт same-card rescue сверх exact `limit/used/remaining 0/0/0`
- **THEN** deterministic verification отклоняет replacement до semantic review
  или publication
- **AND** authorization ceiling `301` не разрешает production line 301,
  repair, другой successor или protocol waiver

#### Scenario: Fast-forward завершает только rescue decision
- **WHEN** `$changerail-ff` подготавливает
  `rescue-git-commit-header-compatibility-decision`
- **THEN** создаются или обновляются только rescue card и proposal, design,
  release-CI delta и tasks этого change
- **AND** production/test/runtime additions остаются zero и не выполняются
  authorization, replacement, implementation, history scan, full baseline, archive,
  review, commit или push
