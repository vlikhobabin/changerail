# Исследовать rescue для целостности phase-routed resume

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Независимый review cycle 3 карточки
  `implement-phase-routed-delivery-authorization-boundary` завершился `NO-GO`:
  пять blocker findings, а same-card rescue budget исчерпан `2/2`.
- Reviewed payload fingerprint:
  `sha256:0b87cc07290bf2a85bdfa2a982ed42ebd593275a78d142bcda15f84de29c7731`.

## Summary
Опубликовать decision-only investigation для linked replacement текущего
phase-routed payload. Исследование должно выбрать один bounded contract для
exact effective `no-push`, производного repair budget, многоуровневой
`resume_from` lineage и unique canonical workspace roots, а затем назвать
точные authorization и implementation successors.

Текущий `NO-GO` payload является входом исследования, но не получает третий
same-card repair и не разрешён к публикации или pilot wave.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Карточка decision-only: production runner, schemas и runtime behavior не
изменяются.

## Depends On
- none

## Blocks
- Создание и выполнение exact replacement
  `replace-phase-routed-resume-integrity-boundary`.
- Публикацию exact authorization source
  `authorize-bounded-phase-routed-resume-integrity-payload`.
- Публикацию отклонённого payload
  `implement-phase-routed-delivery-authorization-boundary`.
- Двухкарточный pilot wave phase-routed batch runner.

## Decision Questions
- Как production child command должен канонически разбираться и сравниваться,
  чтобы terminal receipt принимал ровно один effective `--no-push` и отклонял
  отдельный, объединённый или иной conflicting push argument.
- Как `repair_cycles_used` однозначно выводится из полного ordered history и
  сверяется с `max_repair_cycles` до создания resume authority, preflight,
  lock или model child launch.
- Как представить и проверить полную цепочку `resume_from`, чтобы каждый
  inherited receipt оставался связан со своим фактическим aggregate parent,
  включая не менее двух последовательных `BLOCKED` resume.
- Где plan admission должен отклонять разные aliases, разрешающиеся в один
  canonical Git workspace root, до aggregate status и child preflight.
- Достаточно ли исправления существующих contracts или нужен versioned wire
  field; новые поля допускаются только при явном доказательстве необходимости.
- Какой production LOC ceiling нужен для полного replacement поверх reviewed
  delta 488 LOC. Выбрать минимальный bounded ceiling с проверяемым запасом;
  если одна карточка не укладывается без ослабления invariants, определить
  ordered split и exact successors.

## Selected Decisions

### Exact argv и effective no-push

- Direct phase child принимает только exact delivery-argument vector
  `["--no-push"]`; omitted, duplicate, `--push`, `--no-push=<value>`, отдельные
  conflicting elements и combined string `"--no-push --push"` отклоняются как
  tokens/array mismatch, а не ищутся substring-проверкой.
- Retained terminal `command.argv` полностью повторно выводится из validated
  plan route, workflow, canonical card path, launcher contract и canonical
  discovery prompt, сравнивается по длине и element equality; invocation line
  дополнительно разбирается в exact tokens
  `["$changerail-<phase>", "<canonical-card-path>", "--no-push"]`.
- Любая retained command mutation отклоняет resume до нового
  `RUNNING/resuming` parent, child preflight, lock и model launch.

### Производный repair count

- Один state-machine replay проходит весь ordered `phase_history` от
  `start_phase`, валидирует каждый phase/attempt/result/child receipt и выводит
  `repair_cycles_used` только из допустимых `review/NO-GO -> repair`
  transitions.
- Same-phase `BLOCKED` retries не расходуют новый repair cycle. Persisted
  `repair_cycles_used` остается required observable cache, но дает authority
  только при exact равенстве replayed value и `0..max_repair_cycles`.
- Replay применяется к terminal parent, resume, running child preflight и
  aggregate transition. Mismatch или продолжение после exhausted/terminal
  state отклоняется до новой resume authority, preflight, lock или launch.

### Recursive resume lineage ownership

- `resume_from` остается immediate adjacency link. Validator следует всей
  chain до initial aggregate, на каждом hop проверяет canonical path, schema,
  linked run id, exact status fingerprint, plan identity и отсутствие cycles.
- Для chain oldest-to-newest history нового aggregate обязан иметь exact
  immutable predecessor prefix. Segment
  `[len(previous_history):len(current_history)]` принадлежит current aggregate,
  и каждый child `phase_authority.parent_status` указывает на canonical status
  именно этого owner.
- После `aggregate-1 FF/BLOCKED -> aggregate-2 FF/BLOCKED` aggregate 3
  возобновляет FF attempt 3, сохраняя owners первых двух receipts; successful FF
  достигает DO attempt 4. Truncation, reorder, fork, cycle, stale fingerprint
  или owner rebinding fail closed до launch.

### Canonical Git workspace roots

- Operational workspace identity равен filesystem-normalized результату
  `git -C <declared-path> rev-parse --show-toplevel`; declared path остается
  provenance, а existing status `workspace.root` хранит canonical Git root.
- Разные aliases одного literal path, symlink-target или subdirectories одного
  worktree считаются duplicate canonical root и отклоняются в
  `check_plan_semantics` до aggregate authority/status, child preflight, lock и
  model launch. Distinct canonical roots остаются допустимыми.

### Wire/schema и atomicity

- Дополнительный versioned field не нужен: existing unpublished v1 candidate
  fields `phase_routing`, `resume_from`, workspace `root`,
  `phase_history`/`repair_cycles_used`, payload identity, `workflow`,
  `phase_authority` и `command.argv` достаточны. Schema проверяет shape/ranges,
  а cross-record invariants — production semantics.
- Overall replacement все равно объявляет new authority/wire protocol, потому
  что candidate не опубликован. Schema writer, aggregate transition,
  validator и connected probes публикуются одной atomic карточкой; split,
  создающий промежуточный несовместимый writer/validator, отвергнут.
- Reviewed candidate содержит 488 added production LOC. Exact ceiling нового
  successor равен 500, то есть остается 12 строк измеряемого headroom; residual
  fixes заменяют/консолидируют flawed logic. Production delta `>=501`
  останавливает delivery для новой split investigation без ослабления tests,
  source classification или invariants.

### Exact successors и authorization

- Implementation successor id:
  `replace-phase-routed-resume-integrity-boundary`; initial path
  `openspec/board/2.todo/replace-phase-routed-resume-integrity-boundary.md`;
  authorization/review path
  `openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md`.
- Authorization id:
  `authorize-bounded-phase-routed-resume-integrity-payload`; initial path
  `openspec/board/2.todo/authorize-bounded-phase-routed-resume-integrity-payload.md`;
  published path
  `openspec/board/4.done/authorize-bounded-phase-routed-resume-integrity-payload.md`.
- После публикации этого investigation exact authorization object:
  `{"investigation_card":"openspec/board/4.done/investigate-phase-routed-resume-integrity-rescue.md","investigation_id":"investigate-phase-routed-resume-integrity-rescue","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
- Старая authorization не совпадает по investigation/successor identity и не
  переиспользуется. Новый successor объявляет risk `critical`, new
  authority/wire `yes` и repeated defect class `yes`.

### Connected regression floor

- Для каждого R1/R2/R4 negative probe отдельный canonical base сначала проходит
  тот же production boundary; затем меняется ровно один token/field и
  проверяются exact structured rejection reason, отсутствие новой
  `RUNNING/resuming` authority/lock и `model_launch_delta: 0`.
- R1 покрывает direct и retained omitted, duplicate, reordered, separate и
  combined push args; R2 — budgets 0 и >0, independent count/history mutation,
  exhaustion и repeated `BLOCKED` одного repair; R4 — literal/symlink/subdir
  duplicate roots и distinct-root positive.
- R3 positive выполняет два consecutive real `BLOCKED` resumes, проверяет owner
  каждого receipt и достигает DO attempt 4. Hop run/path/fingerprint,
  prefix/order/cycle/owner mutations являются отдельными zero-launch
  negatives.
- Fake launcher управляет только deterministic terminal outcomes; aggregate
  admission и single-card authority всегда проверяет production runner.

## Acceptance
- Для cycle-3 R1-R4 выбрано по одному fail-closed production решению; R5
  преобразован в обязательную connected regression matrix.
- Exact command policy сравнивает разобранные argv/effective flags, а не
  substring, и отклоняет любой push authority до model launch.
- Repair count является производным от валидированной истории и не может быть
  независимо подменён в retained parent.
- Lineage contract валидирует всю ordered `resume_from` chain и сохраняет
  actual aggregate owner каждого receipt через два и более resume hops.
- Canonical workspace root уникален внутри plan независимо от alias; duplicate
  root отклоняется до mutation boundary.
- Для каждого negative probe требуется доказанный passing canonical base,
  точная причина rejection и `model_launch_delta: 0`; positive nested-resume
  probe достигает ожидаемой следующей фазы.
- Измерен production delta текущего candidate и выбран exact bounded ceiling
  либо ordered split. Ослабление source classification или тестов запрещено.
- Названы exact successor id/path и отдельная authorization-карточка с полным
  шестиполевым authorization object; старая authorization не переиспользуется.
- Investigation не изменяет production code, schemas, tests или runtime
  behavior и проходит fresh independent review до создания successors.

## Non-Goals
- Делать третий repair карточки
  `implement-phase-routed-delivery-authorization-boundary`.
- Публиковать или запускать текущий `NO-GO` payload.
- Сбрасывать review history или увеличивать same-card rescue budget.
- Ослаблять `no-push`, dirty-worktree, payload fingerprint или same-user
  tampering boundaries.
- Добавлять cryptographic trust для локальных runtime artifacts.

## Change Set
- `decide-phase-routed-resume-integrity-rescue`

## Verify
- `bin/openspec validate decide-phase-routed-resume-integrity-rescue --strict` —
  passed before sync; retained evidence `openspec-change-strict-pre-sync`.
- `bin/openspec validate changerail-delivery-runner --strict` and
  `bin/openspec validate --all --strict` — passed after sync; retained evidence
  `capability-strict-post-sync` and `all-strict-post-sync`.
- `python3 scripts/public-surface-scan.py` — passed; retained evidence
  `public-surface-scan`.
- `python3 -m json.tool .mcp.json` and TOML parse `.codex/config.toml` —
  passed; retained evidence `mcp-json-parse` and `codex-toml-parse`.
- `git diff --check` and separate `git diff --no-index --check` scan of each
  new card/archive artifact — passed; retained evidence `tracked-diff-check`
  and `untracked-whitespace-scan`.
- Evidence index:
  `.runtime/changerail/evidence/investigate-phase-routed-resume-integrity-rescue/index.json`.

## Archive
- `openspec/changes/archive/2026-08-23-decide-phase-routed-resume-integrity-rescue/`

## Related
- `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/4.done/investigate-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `openspec/changes/archive/2026-08-23-decide-phase-routed-resume-integrity-rescue/`

## Result
Decision-only investigation delivered: selected fail-closed contracts for exact
`--no-push`, replay-derived repair usage, recursive receipt ownership and
canonical Git roots are retained in the card and archive. Synced exactly one
`changerail-delivery-runner` decision requirement. Production code, schemas,
tests, CLI, public runtime docs and runtime behavior remain unchanged.
Exact replacement and authorization cards are deliberately not created before a
fresh independent `GO` and publish of this investigation.

Repair attempt 1 исправил только stale statement archived proposal: он явно
допускает единственную apply-phase синхронизацию task 2.1 в main spec, сохраняя
decision-only boundary без production/runtime, successor или authorization
изменений. Cycle-1 `NO-GO` сохранён в review history; fresh independent review
cycle 2 завершился `GO` с 12/12 пройденными acceptance criteria и без findings.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-phase-routed-resume-integrity-rescue`

### Why
После двух bounded repairs fresh cycle-3 review воспроизвёл четыре остаточных
defect класса в child authority, resume history/lineage и workspace admission.
Старая exact authorization исчерпана по successor identity и почти по LOC
ceiling, поэтому продолжение требует нового опубликованного решения.

### Goal
Зафиксировать минимальный целостный contract и bounded verification floor для
новой linked replacement-карточки без изменения production behavior.

### Scope
- Воспроизвести и классифицировать cycle-3 R1-R5 против tracked contracts.
- Выбрать exact command, repair-count, recursive-lineage и workspace-root
  invariants.
- Измерить необходимый production ceiling и решить atomic versus ordered split.
- Назвать exact implementation и authorization successors и их reciprocal
  relations.
- Не изменять runner, schemas или tests в decision-only change.

### Acceptance
- Все `Decision Questions` получают однозначное решение и rejected
  alternatives.
- Каждый blocker связан с production boundary и обязательным connected probe.
- Successor cards могут быть созданы и запущены без дополнительного
  продуктового решения оператора.

### Depends On
- none

### Related
- `openspec/changes/decide-phase-routed-resume-integrity-rescue/`

## Log
- 2026-08-23T01:22:17Z создана после fresh cycle-3 `NO-GO`; исходная карточка
  исчерпала две разрешённые same-card rescue attempts.
- 2026-08-23T01:35:46Z `$changerail-ff` выбрал exact command, derived repair,
  recursive lineage и canonical-root contracts, atomic ceiling 500, exact
  successor/authorization chain и connected regression floor; созданы
  apply-ready artifacts без production/runtime изменений.
- 2026-08-23T01:42:10Z `$changerail-do` синхронизировал единственный decision
  requirement, архивировал change, сохранил deterministic verification evidence
  и оставил карточку в `3.inprogress` для fresh independent review.
- 2026-08-23 repair attempt 1: исправлено только R1 в archived `proposal.md`;
  refreshed deterministic evidence, manifest scope и normalized preflight
  подготовлены для fresh review cycle 2, без изменения cycle-1 verdict/history.
- 2026-08-23T04:59:36Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
