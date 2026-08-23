## Context

Rejected cycle-3 payload сохраняет выбранный ранее phase-routed
aggregate/child protocol и добавляет 488 production-counted строк в
`bin/changerail-delivery-runner`, но fresh review воспроизвел четыре
независимых integrity defects:

- terminal `command.argv` принимается по substring `--no-push`, поэтому
  conflicting `--push` может сохранить dirty-child authority;
- сохраненный `repair_cycles_used` не сверяется с полным ordered history;
- только immediate `resume_from` parent назначается owner всех inherited
  receipts, что ломает второй последовательный `BLOCKED` resume;
- plan aliases не проверяются на один canonical Git worktree root.

Passing smoke не наблюдал эти boundaries. Same-card rescue budget исчерпан, а
предыдущая authorization связана с другим successor id. Поэтому текущий change
публикует только решение и verification floor для нового replacement; runtime
payload остается read-only investigation input.

Ограничения репозитория: global ordinary ceiling равен 300 added production
LOC, bounded authorization допускает только `301..500`, runtime artifacts не
трекатся, а fully coordinated same-user rewrite без внешнего trust anchor
остается вне non-cryptographic contract.

## Goals / Non-Goals

**Goals:**

- Однозначно определить exact effective `no-push` для direct child admission
  и retained terminal receipt.
- Сделать repair usage производным от одного deterministic replay ordered
  history и проверить его до любой новой resume authority.
- Проверять всю `resume_from` chain и назначать каждому receipt его
  фактический aggregate owner через два и более resume hops.
- Использовать unique canonical Git top-level как workspace identity до
  aggregate mutation.
- Выбрать wire/schema impact, atomicity, exact successor/authorization paths,
  bounded LOC ceiling и connected regression probes.

**Non-Goals:**

- Исправлять или публиковать rejected candidate в этом change.
- Добавлять третий repair исходной карточки, сбрасывать history или повышать
  same-card rescue budget.
- Добавлять cryptographic signatures, privileged runtime writer или reusable
  authorization для будущих protocols.
- Ослаблять source classification, canonical path, dirty payload fingerprint,
  test oracle или model-launch boundary.

## Decisions

### 1. Exact child command является re-derived structured authority

Direct phase child принимает только exact parsed delivery-argument vector
`["--no-push"]`. Пустой vector, duplicate `--no-push`, `--push`,
`--no-push=<value>`, отдельные conflicting elements и один combined string
`"--no-push --push"` отклоняются. Проверка выполняется над tokens/array
equality, а не `in`/substring.

Retained terminal receipt проверяется сильнее: validator повторно строит
канонический expected Codex argv из validated plan route, workflow, canonical
card path, launcher contract и единственного `--no-push`, сравнивает JSON argv
по длине и element equality, затем разбирает invocation line prompt в exact
tokens
`["$changerail-<phase>", "<canonical-card-path>", "--no-push"]`.
Остальной canonical discovery-policy prompt также должен совпасть с
re-derived value. Любой extra, missing, reordered, combined или conflicting
push token дает отдельный command-authority diagnostic. На resume такой
retained mismatch отклоняется до записи нового `RUNNING/resuming` parent,
production child preflight, lock или model launch.

Rejected: считать элементы, содержащие substring. Rejected: проверять только
`command.model`/`reasoning_effort` и доверять prompt prose. Exact re-derivation
уже возможна из parent и tracked plan и не требует нового wire field.

### 2. Repair usage выводится replay state machine, а поле является cache

Один validator проходит полный ordered `phase_history` от declared
`start_phase`, начиная с `used=0` и expected attempt 1. Каждый receipt обязан
совпасть с expected phase/attempt, schema-valid child status и разрешенным
transition:

- `ff/DELIVERED -> do`, `do/DELIVERED -> review` и
  `repair/DELIVERED -> review`;
- `review/NO-GO -> repair` увеличивает `used` ровно один раз только когда
  `used < max_repair_cycles`;
- `BLOCKED ->` та же phase на следующем resume attempt и не расходует repair;
- `review/NO-GO` при `used == max_repair_cycles`, successful review и иные
  terminal states запрещают дальнейшие receipts.

После replay computed `used`, next phase/attempt и terminality сравниваются с
retained card. Required wire field `repair_cycles_used` сохраняется для
observability/schema compatibility, но authority получает только при exact
равенстве derived value. Два `BLOCKED` retries одной repair phase не считаются
двумя repair cycles. Этот validator используется terminal-parent admission,
resume, running-parent child preflight и aggregate transition; local defaults
или отдельные формулы запрещены.

Mismatch с budget/history отклоняется до нового canonical resume parent,
single-card preflight, lock и model child launch. Диагностический `BLOCKED`
result может быть возвращен вызывающему процессу, но не является dirty-child
authority.

Rejected: доверять retained count. Rejected: считать repair receipts, потому
что повторный same-phase `BLOCKED` resume создает несколько receipts одного
semantic repair cycle. Rejected: считать только последний predecessor.

### 3. `resume_from` остается adjacency link, а owner выводится рекурсивно

Новый versioned lineage field не добавляется. Для current aggregate validator
рекурсивно следует каждому immediate `resume_from` до initial parent и на
каждом hop проверяет canonical aggregate path under the same consumer root,
regular non-symlink status, schema, linked run id, exact status fingerprint,
plan identity/fingerprint и отсутствие path/run cycles.

После разворота chain oldest-to-newest для каждой card проверяется, что history
нового aggregate имеет exact immutable prefix previous history. Receipt
segment `[len(previous_history):len(current_history)]` принадлежит current
aggregate; для initial parent segment начинается с нуля. Каждый receipt и
terminal child status обязан ссылаться через `phase_authority.parent_status`
на canonical path именно своего segment owner. Resume hop дополнительно
сохраняет payload, workspace/card identity и derived repair usage, а latest
receipt обязан быть real same-phase `BLOCKED`; новый attempt равен `N+1`.

Таким образом chain
`aggregate-1/BLOCKED -> aggregate-2/BLOCKED -> aggregate-3/RUNNING`
оставляет первый receipt у aggregate 1, второй у aggregate 2 и только новый
segment у aggregate 3. Chain truncation, reorder, fork, cycle, wrong immediate
fingerprint или owner rebinding fail closed до dirty launch.

Rejected: назначать immediate predecessor owner всего inherited prefix.
Rejected: копировать owner в каждый receipt новым wire field — существующие
`resume_from`, history boundaries и child `phase_authority` уже дают
однозначный derivation и избегают дублируемой tamperable authority.

### 4. Workspace identity — unique canonical Git top-level

Plan semantics разрешает declared workspace path, затем вызывает
`git -C <resolved-path> rev-parse --show-toplevel` и нормализует returned path
через filesystem resolution. Это значение является canonical Git workspace
root, записывается в существующий status `workspace.root` и передается child.
Declared `workspace.path` остается provenance.

Внутри одного plan два aliases не могут иметь одинаковый canonical Git root.
Одинаковый literal path, symlink path и разные subdirectories одного worktree
считаются duplicate root. Проверка выполняется вместе с `check_plan_semantics`
до создания canonical aggregate authority/status, production child preflight,
workspace lock или model launch. Она применяется и к monolithic plan
admission как безопасный identity invariant, не меняя monolithic scheduling.

Rejected: сравнивать только aliases или lexical paths. Rejected: откладывать
проверку до card resolution, потому что одна physical card уже получает две
workspace identities.

### 5. Residual rescue не добавляет новый wire version

Replacement сохраняет unpublished candidate schema ids и его существующие v1
fields: plan `phase_routing`, aggregate `resume_from`, workspace `root`, card
`phase_history`/`repair_cycles_used`/payload/phase identity, child `workflow`,
`phase_authority` и existing `command.argv`. JSON Schema продолжает проверять
shape/ranges/required fields; cross-record command, derived-count, recursive
lineage и canonical-Git-root invariants принадлежат production semantic
validation.

Новый lineage-owner field, repair counter version или schema id не нужен.
Overall successor все равно объявляет `New authority or wire protocol: yes`,
потому что исходный candidate не опубликован и replacement атомарно вводит
phase-routed v1 writer/validator contract. Public docs и delta spec должны
описывать тот же contract.

### 6. Один atomic replacement остается bounded ceiling 500

Exact implementation successor:

- id: `replace-phase-routed-resume-integrity-boundary`;
- initial path:
  `openspec/board/2.todo/replace-phase-routed-resume-integrity-boundary.md`;
- authorization/review path:
  `openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md`.

Exact authorization source:

- id: `authorize-bounded-phase-routed-resume-integrity-payload`;
- initial path:
  `openspec/board/2.todo/authorize-bounded-phase-routed-resume-integrity-payload.md`;
- published path:
  `openspec/board/4.done/authorize-bounded-phase-routed-resume-integrity-payload.md`.

Published investigation path:
`openspec/board/4.done/investigate-phase-routed-resume-integrity-rescue.md`.
Authorization source MUST содержать ровно один six-field object:

```json
{"investigation_card":"openspec/board/4.done/investigate-phase-routed-resume-integrity-rescue.md","investigation_id":"investigate-phase-routed-resume-integrity-rescue","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Старая `authorize-bounded-phase-routed-delivery-payload` не совпадает по
investigation/successor identity и не переиспользуется. Successor должен
содержать exact published-authorization reference на новый source, зависеть от
этого investigation и объявлять risk `critical`, new authority/wire `yes` и
repeated defect class `yes`.

Atomic delivery выбрана потому, что schema writer, aggregate transition,
recursive validator и production probes образуют одну dirty-worktree
authority boundary; промежуточный split публиковал бы writer без полного
validator либо validator без schema-valid records. Fresh measurement дает 488
added production LOC; ceiling 500 оставляет 12 строк проверяемого headroom.
Residual fixes должны заменять/консолидировать duplicated candidate logic, а
не добавляться поверх него. Source classification и tests не ослабляются.
Production delta 501 или больше останавливает successor для новой
investigation/split authorization; automatic split или повышение ceiling не
разрешены этим решением.

### 7. Connected regression matrix является release boundary

Каждый negative probe начинает с собственного fresh canonical fixture или
клона одного доказанно passing base. До mutation test явно доказывает, что
unmodified base проходит тот же production boundary. Затем изменяется только
названный field/token; assertion проверяет structured exact rejection reason,
отсутствие нового `RUNNING/resuming` authority, lock и
`model_launch_delta: 0`.

| Finding | Connected production probes | Required outcome |
| --- | --- | --- |
| R1 | Direct omitted, duplicate, separate и combined push args; retained terminal argv с removed/reordered/extra/combined `--no-push`/`--push`; unmodified terminal base | Exact re-derived argv/base passes; каждая mutation дает command-authority rejection и zero launch |
| R2 | Budgets 0 и >0; independent retained count `-1/+1`; history with missing/extra/reordered review `NO-GO` or repair; repeated `BLOCKED` in one repair | Replay-derived value/base passes; mismatch/exhaustion rejects before resume authority with zero launch |
| R3 | Two consecutive real FF `BLOCKED` resumes; per-segment parent assertions; hop run/path/fingerprint, prefix, order, cycle and owner mutations | Third aggregate resumes FF attempt 3 and reaches DO attempt 4; every isolated lineage mutation rejects with zero launch |
| R4 | Distinct roots pass; same literal root, symlink root and different subdirectories of one Git top-level under distinct aliases | Duplicate canonical root rejects in plan semantics before aggregate status/preflight/lock/launch |
| R5 | Matrix harness records canonical-base result, mutation id, expected/actual reason and launch counter for every row; production runner owns admission | Full smoke cannot pass on disconnected invalid base; fake launcher controls terminal outcome only |

Positive nested-resume probe uses production aggregate and production
single-card preflight. A fake Codex launcher may deterministically return the
two `BLOCKED` outcomes, FF `DELIVERED` and next-phase outcome, but it cannot
replace the production authority validator. It MUST assert that receipts 1 and
2 point to aggregate 1 and 2 respectively, aggregate 3 starts FF attempt 3,
and successful FF transition invokes DO attempt 4.

## Risks / Trade-offs

- [Risk] Recursive lineage validation reads every retained ancestor and may be
  slower for long chains. → Mitigation: validate each unique canonical path
  once, detect cycles, and keep the chain bounded by actual local statuses;
  correctness is preferred over a partial prefix.
- [Risk] `repair_cycles_used` remains a stored field that can be edited. →
  Mitigation: it is non-authoritative until exact equality with replayed state
  is proven at every authority boundary.
- [Risk] 12-line ceiling headroom is narrow. → Mitigation: implement from the
  rejected patch as a replace/consolidate exercise, measure production LOC
  continuously and stop at 501 rather than compress tests or semantics.
- [Risk] Canonical Git top-level collapses declared subdirectories. →
  Mitigation: phase workspaces are repository ownership units; declared path
  remains diagnostic provenance, while duplicate operational ownership is
  rejected early.
- [Risk] Fully coherent same-user rewrite remains possible. → Mitigation:
  preserve the documented non-cryptographic boundary and keep signing or a
  privileged writer out of this successor.

## Migration Plan

1. Deliver, sync, independently review and publish this decision-only change;
   no runtime migration occurs.
2. Create the exact replacement and authorization cards at their declared
   `2.todo` paths with reciprocal investigation relations; do not reopen the
   rejected card.
3. Build the atomic replacement from the rejected input, move it through
   `3.inprogress`, and continuously prove production LOC `<=500` plus the full
   connected matrix. Stop for a new split investigation if the ceiling fails.
4. Publish the separate authorization source with the exact object only after
   its investigation/successor path relations are valid, then run fresh
   critical independent review of the replacement.
5. Permit no pilot wave until successor review and publish complete.

Rollback for this investigation is documentation-only. Later implementation
rollback must revert the atomic schema/writer/validator payload together.

## Open Questions

- none
