## Context

Published structural investigation `8adddfe` и authorization `644e9e1` разрешили
bounded history-scanner successor. Unpublished successor исчерпал ремонт
после того, как его synthetic commit-header parser отклонил valid
GitHub-signed merge `4fb01e7a12c43ab5c5ff06b1388743433846b54d`. В folded
`gpgsig` этого commit есть valid exact physical continuation `b" "`.

Первая linked investigation затем точно описала compatibility grammar и
read-only evidence, но при sync в main spec один existing auth scenario попал
в новый requirement. Её review/repair budget исчерпан. Этот rescue
стартует от clean published `644e9e1bf03fa444d603652b17d7262846149978`,
заново авторизует только decision facts и не переносит exhausted
card/archive/evidence в published lineage.

## Goals / Non-Goals

**Goals:**

- Задать total bounded raw commit-header byte grammar, принимающую valid
  blank folds без parsing identity, parent или signature contents.
- Закрепить exact 95-commit source ancestry и pinned 98-commit all-ref model,
  digests и aggregate observations.
- Сделать existing auth requirement и new Git-header requirement недвусмысленно
  разделёнными по heading boundaries и scenario counts.
- Определить clean rescue investigation -> authorization -> unchanged
  replacement lineage.

**Non-Goals:**

- Исправлять, архивировать, публиковать или задним числом принимать
  exhausted decision и scanner payload.
- Определять semantic grammar для `parent`, `author`, `committer`,
  `encoding`, `gpgsig`, `mergetag` или unknown later headers.
- Менять published structural batch, tree, path, reachability, memoization,
  findings и no-mutation contracts.
- Создавать authorization/replacement cards или executable payload; запускать
  history scan, benchmark или full release baseline.

## Decisions

### 1. First tree и first-SP framing образуют минимальную grammar

Replacement получает уже batch-validated raw commit body. Первый `LF LF`
отделяет header block от arbitrary message:

```text
commit       = tree_line LF *(later_line LF) LF message
tree_line    = "tree" SP HEX40
later_line   = initial_line | continuation_line
initial_line = key SP value_fragment
continuation_line = SP value_fragment
key          = 1..255 bytes in 0x21..0x7e
value_fragment = 0..N opaque bytes excluding 0x00..0x1f and 0x7f
```

`HEX40` состоит ровно из 40 lowercase ASCII hex bytes. В initial line
первый `SP` завершает key, а весь remainder является opaque value.
Value может быть empty, содержать further spaces и bytes `0x80..0xff`.
Continuation может быть exact `b" "`, но только после later
non-`tree` logical header. Continuation сразу после semantic tree или
без preceding later header invalid.

Complete commit body ограничен `64 MiB`, header block `64 MiB - 2`,
а physical-line count `1,000,000`. Это internal constants, не config/CLI/wire
surface. Missing separator, missing first `SP`, bad tree placement, NUL/control/DEL
в header value, bad key byte/length и exact one-over bounds fail closed до output.

Альтернативы с non-empty folds, whitelist keys или parsing signature/identity
отклонены: они снова вводят synthetic Git subset.

### 2. Только first tree OID имеет semantics

Первая physical line обязана быть exact tree line. Missing, late,
duplicate или continued tree, а также uppercase/short/long/non-hex OID дают
hard failure. All later headers framing-validated, но их names и values не
интерпретируются. Это оставляет traversal строгим, но не вводит
failure modes для compatibility data.

### 3. Pinned model evidence имеет две явно разные populations

Read-only model принял exact source ancestry
`git rev-list 644e9e1bf03fa444d603652b17d7262846149978`: `95/95`, rejects `0`,
ordered digest
`sha256:8576a6f652fa2d168d0956ff225471c92b5190fc46cef707bdae2472584b86ba`,
sorted digest
`sha256:0771d6bc5ad5f121ac630d58805eba30185e84f53595c6ec117f5138ca597eb7`.

Separately pinned planning `git rev-list --all` population: `98/98`, rejects `0`.
Она добавляет OIDs `e0ec75135e8a35be5283a9d6de556dc63f43e260`,
`e2a39bec92a165a63ede6e3835dc03807fd6ff8f` и
`e7f5542d91aad1c79545f6a2239f87d3761e9180`; ordered digest
`sha256:31c8ae5d7a32a748e5efd371c63d2ae622949d1c8c7c8241c730dd3678c0460e`,
sorted digest
`sha256:f0545cd40fb856e5153821988a9156941c519c8738abdc11088362b0f58c425d`,
sorted ref snapshot
`sha256:5b53eac521b1d0618949bbbc2b89b86c5adb4b208c307ca53bd78baac180fad5`.

Каждая population имеет три signed commits, 48 continuation lines и шесть
exact blank folds. Counts не приписываются трём extra-ref commits. Это
decision input, а не new public-history PASS или replacement evidence.

### 4. Requirement ownership проверяется по heading slices

Delta добавляет один complete Git-header requirement с ровно восемью
scenarios. При sync он размещается после complete existing
`Consumer Codex auth setup smoke coverage` requirement. Deterministic oracle
выделяет каждый block от `### Requirement:` до следующего heading:

- auth block имеет ровно два scenarios и включает
  `Smoke keeps credentials out of output`;
- Git-header block имеет ровно восемь scenarios и не получает auth-fixture
  scenario.

Обычный broad substring count отклонён: он не доказывает ownership.

### 5. Successor fixtures проверяют raw objects и full structural matrix

Future replacement создаёт real raw commit objects для tree-only, unknown
printable keys, empty initial values, multiple/blank folds в unknown/`gpgsig`/
`mergetag`, high-byte values и exact bounds. Negative matrix покрывает
missing/late/duplicate/bad tree, orphan fold, missing first `SP`, bad key/value
bytes, missing separator и exact one-over body/header/key/line limits. Further
`SP` после separator остаётся opaque value, а не negative key case.

Этот matrix дополняет, а не ослабляет published exact-two-child batch,
fault injection, independent ordered tuples, legacy parity, no-partial-output и
byte-identical refs/worktree/index no-mutation checks.

### 6. Clean authorization ссылается на rescue ID

После publication этого decision отдельная card
`authorize-bounded-git-commit-header-compatible-history-scan` публикует
ровно такой object:

```json
{"investigation_card":"openspec/board/4.done/rescue-git-commit-header-compatibility-decision.md","investigation_id":"rescue-git-commit-header-compatibility-decision","successor_card":"openspec/board/3.inprogress/deliver-git-compatible-structural-public-history-scan-replacement.md","successor_id":"deliver-git-compatible-structural-public-history-scan-replacement","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

Только после remote-reachable clean authorization можно создать unchanged
replacement с exact two-field authorization reference. Replacement добавляет
`<=300` production LOC относительно `ccccb62562e1646b595119edd3326763860f14a7`,
не вводит authority/protocol, имеет `critical`/`xhigh`, repeated `yes` и
terminal rescue budget `0/0/0`, exhausted `true`. Ceiling `301` gate не
разрешает production line 301.

## Risks / Trade-offs

- **[Risk] Opaque later headers могут быть semantically invalid.** -> Scanner
  использует только exact first tree; Git object integrity и reachability проверяются
  отдельно.
- **[Risk] Control-byte prohibition может отклонить future valid counterexample.** ->
  Current pinned populations полностью приняты; новый counterexample требует
  новой investigation, а не silent relaxation.
- **[Trade-off] Parser не валидирует parent OIDs.** -> Traversal следует
  fresh `rev-list --all`, поэтому parent semantics не защищает tree decision.

## Migration Plan

1. Deliver, independently review и publish только этот docs-only rescue.
2. Создать и publish exact clean authorization с rescue investigation ID.
3. Создать clean replacement из published lineage и выполнить его
   indivisible verification floor.
4. При любом implementation/review failure остановить replacement без
   same-card repair. Rollback остаётся на published safe production `ccccb625`.

## Open Questions

Нет. Grammar, evidence populations, ownership oracle, lineage, ceiling и review
route зафиксированы.
