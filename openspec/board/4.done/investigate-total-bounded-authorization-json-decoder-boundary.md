# Исследовать total bounded JSON decoder для authorization

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
- Неопубликованная карточка
  `authorize-type-safe-phase-routed-resume-integrity-payload` получила
  independent cycle 3 `NO-GO`; blocker `R6`, reviewed fingerprint
  `sha256:04f98908eb49c4b221ccf159097bfe75109ffb4edf122c4a210ca79c25fb101b`.
- Same-card rescue budget исчерпан `2/2`.
- `R6`: valid JSON integer из 4301 цифры проходит текущие length/nesting/comma
  limits, но decoder outcome/detail зависит от CPython
  `PYTHONINTMAXSTRDIGITS`.
- Sol `xhigh` escalation дополнительно установил, что `JSONDecoder` принимает
  non-standard `NaN`/`Infinity`, а adjacent inline
  `Published investigation authorization` по-прежнему использует unrestricted
  `json.loads` и может выпустить `RecursionError`.
- Latest published safe dependency:
  `openspec/board/4.done/investigate-type-safe-decoded-target-classification-boundary.md`,
  commit `fee971636088bd57710160f40c316f6ef601ff5c`.

## Summary
Опубликовать decision-only investigation, которая выберет один strict,
total/non-throwing и resource-bounded JSON decoder contract для двух ролей:
source values поля `Investigation authorization` и inline reference поля
`Published investigation authorization`. Решение фиксирует parser-owned
numeric lexemes, exact per-value/aggregate limits, stable details, role-specific
identity validation и единственную replacement authorization identity.

Failed payload является только forensic input. Карточка не repair-ит и не
копирует его, не создает replacement authorization card или downstream
successor и не меняет runtime surface.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Decision-only scope не является новой authorization authority. Authority может
появиться только в отдельной поздней опубликованной карточке с выбранной ниже
identity.

## Depends On
- `investigate-type-safe-decoded-target-classification-boundary`

## Blocks
- Дальнейший repair или publication failed payload
  `authorize-type-safe-phase-routed-resume-integrity-payload`.
- Создание и delivery
  `authorize-total-bounded-phase-routed-resume-integrity-payload`.
- Создание и delivery `replace-phase-routed-resume-integrity-boundary`.
- Продолжение pilot wave phase-routed batch runner.

## Decision Contract
- Strict JSON отклоняет `NaN`, `Infinity` и `-Infinity` с detail
  `authorization JSON must not contain NaN or Infinity`.
- Decoder сохраняет numeric token как validated lexeme и не вызывает `int()`
  или `float()` до role-specific type validation. Numeric lexeme ограничен 64
  ASCII characters вместе со знаком, fraction point и exponent; overflow дает
  `authorization JSON number exceeds 64 characters` независимо от
  `PYTHONINTMAXSTRDIGITS`.
- Каждый normalized field value ограничен 4096 Unicode code points, 255 JSON
  lexical tokens и nesting depth 16. На один Markdown document допускается не
  более 16 exact role fields, 16384 aggregate code points и 1020 aggregate
  tokens.
- Общие resource details: `authorization JSON value exceeds 4096 characters`,
  `authorization JSON value exceeds 255 tokens`,
  `authorization JSON value exceeds nesting depth 16`,
  `authorization fields exceed 16 values`,
  `authorization JSON aggregate exceeds 16384 characters` и
  `authorization JSON aggregate exceeds 1020 tokens`.
- Universal single-pass first-failure order фиксирован для обеих roles: field
  count, aggregate characters, per-value characters, prohibited
  `NaN`/`Infinity`/`-Infinity`, generic RFC 8259 syntax, numeric lexeme length,
  nesting depth, per-value tokens, aggregate tokens. Earlier item wins на одном
  field/code-point/scanner/token event; parser immediately stops without
  fallback/rollback, а role checks начинаются после universal stage.
- Поэтому 17th field wins над его content; aggregate chars wins над per-value
  chars и token на том же code point; constant, syntax, numeric и depth win в
  declared order before tokens; per-value token wins над aggregate token. После
  трех 255-token values valid fourth 257-token value получает
  `authorization JSON value exceeds 255 tokens` на token 256, хотя aggregate
  reaches 1021. Future generated collision rows cover these field/character/
  resource ties for source и inline при `PYTHONINTMAXSTRDIGITS=640` и `0`.
- Universal extraction/resource/decode stage выполняется до role-specific
  cardinality/schema checks. Source role допускает bounded sequence values для
  published pair-preserving target selection. Inline role требует ровно один
  two-field reference object или literal `none`; обе роли сохраняют decoded
  pairs и не используют unvalidated identity values в hashing, path или
  semantic relation operations.
- Единственная replacement identity:
  `authorize-total-bounded-phase-routed-resume-integrity-payload`. Ее future
  published source связывает эту investigation с
  `replace-phase-routed-resume-integrity-boundary`, ceiling 500 и protocol
  allowance `true`; successor позднее ссылается только на exact published
  replacement source.

## Acceptance
- Card и один active OpenSpec change фиксируют все numeric, per-value и
  aggregate ceilings, точное правило token/depth/count accounting и stable
  details без зависимости от interpreter limits.
- Strict constants, integer boundaries 64/65 characters, signs, fractions,
  exponents, malformed number grammar, depth 16/17, token 255/257, chars
  4096/4097, aggregate field count 16/17 и aggregate char/token boundaries
  представлены observable downstream scenarios для обеих field roles.
- Observable collision scenarios define one exact detail for same field,
  character и token events, включая field-count/aggregate-char,
  aggregate-char/per-value-char, character/token, constant/syntax/numeric/depth
  versus token и reviewer 256th-token collision, across both roles and both
  `PYTHONINTMAXSTRDIGITS` environments.
- Future RED/GREEN matrix запускает production `run_preflight` при
  `PYTHONINTMAXSTRDIGITS=640` и `PYTHONINTMAXSTRDIGITS=0` и получает identical
  exact exit/outcome/status/detail/counters для каждой строки, без uncaught
  exception и с нулем semantic/review/model dispatch на decoder/schema reject.
- Role contract различает source candidate sequence и single inline reference,
  но использует один decoder и одинаковые decoder-limit details; exact identity
  fields проверяются как non-empty strings до path/relation semantics.
- Выбраны exact replacement card id/path, reciprocal relations, six-field
  source object, two-field successor reference, ceiling и protocol allowance;
  replacement и successor остаются отсутствующими.
- Investigation delivery изменяет только эту card, один decision change,
  apply-time main-spec sync/archive metadata и проходит docs/spec verification;
  production parser, smoke/tests, schemas, runner, CLI, runtime docs и failed
  payload остаются неизменными.
- Investigation verification и future implementation verification перечислены
  раздельно; implementation floor не выдается за выполненное доказательство
  decision-only payload.

## Non-Goals
- Исправлять или копировать
  `authorize-type-safe-phase-routed-resume-integrity-payload`.
- Изменять `scripts/changerail_review_preflight.py`, smoke/tests, schemas,
  runner, CLI, runtime docs или main spec во время fast-forward.
- Создавать `authorize-total-bounded-phase-routed-resume-integrity-payload` или
  `replace-phase-routed-resume-integrity-boundary`.
- Сбрасывать review history, увеличивать same-card rescue budget, писать новый
  verdict или `GO`; ignored repair manifest/evidence/preflight разрешены только
  для bounded rescue attempt 1.
- Выполнять review, archive, commit, push или publish в этой planning phase.

## Stop Conditions
- Остановить decision delivery, если exact limits/details или role ordering
  изменяются без одновременного обновления card, delta spec и downstream matrix.
- Остановить successor creation, пока эта investigation и отдельная replacement
  authorization card не опубликованы в exact порядке lineage.
- Остановить later implementation при любом различии matrix между
  `PYTHONINTMAXSTRDIGITS=640` и `0`, uncaught exception, semantic/review/model
  dispatch на reject либо отсутствии production-bound counter evidence.
- Остановить работу, если scope требует production parser/test/schema/runtime
  edit в decision change или repair forensic payload.

## Change Set
- `decide-total-bounded-authorization-json-decoder-boundary`

## Verify
### Investigation delivery
- `bin/openspec validate decide-total-bounded-authorization-json-decoder-boundary --strict`
- После apply-time sync: `bin/openspec validate changerail-contracts --strict`
  и `bin/openspec validate --all --strict`.
- `python3 scripts/public-surface-scan.py`.
- `python3 -m json.tool .mcp.json` и TOML parse `.codex/config.toml`.
- `git diff --check`, explicit whitespace scan untracked artifacts и scoped
  diff/status check, доказывающий отсутствие production/runtime/successor files.
- Cycle-1 rescue дополнительно проверяет exact archive/main requirement equality,
  manifest/evidence validation и final non-normalizing review preflight against
  frozen tracked payload.
- RED/GREEN runtime evidence для decision-only payload: `not applicable`,
  потому что change меняет только card/spec decision artifacts.

### Later implementation
- Connected production `run_preflight` matrix отдельно при
  `PYTHONINTMAXSTRDIGITS=640` и `PYTHONINTMAXSTRDIGITS=0` с exact identical
  results для обеих roles и всех boundary rows.
- Existing phase-routed resume-integrity matrix и полный
  `python3 scripts/smoke-review-preflight.py`.
- `python3 scripts/run-release-baseline.py` и
  `bin/changerail-source-classification check --json`.
- `bin/openspec validate --all --strict`, `python3 -m py_compile` для changed
  Python files и `ruff check` when available.
- `python3 scripts/public-surface-scan.py`, `git diff --check` и scoped diff
  checks.

## Handoff Criteria
- Один decision change валиден strict, acceptance и exact limits/details
  совпадают между card/proposal/design/spec/tasks, а active successor отсутствует.
- `$changerail-do` может только финализировать decision docs, синхронизировать
  один `changerail-contracts` requirement, архивировать change и передать
  карточку fresh independent review.
- Только после published `GO` этой investigation можно создать отдельную
  `authorize-total-bounded-phase-routed-resume-integrity-payload`; только после
  ее published `GO` можно создать downstream successor.

## Archive
- `openspec/changes/archive/2026-08-24-decide-total-bounded-authorization-json-decoder-boundary/`

## Related
- `openspec/board/4.done/investigate-type-safe-decoded-target-classification-boundary.md`
- `openspec/changes/archive/2026-08-24-decide-total-bounded-authorization-json-decoder-boundary/`
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`

## Result
Decision-only investigation verified, synced as one `changerail-contracts`
requirement and archived. Cycle-1 `NO-GO` R1 repaired in card/spec docs with a
complete same-event precedence and collision matrix. Fresh independent cycle-2
`gpt-5.6-sol/high` review returned `GO`; cycle-1 `NO-GO` remains preserved in
review history. Production/runtime surface, failed payload, replacement
authorization and downstream successor were not created or changed. Runtime
RED/GREEN is not applicable to this card/spec-only payload.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-total-bounded-authorization-json-decoder-boundary`

### Why
Предыдущий type-safe decision не ограничил numeric conversion и не охватил
adjacent inline reference decoder. Legal 4301-digit integer, non-standard
constants и deep inline input поэтому сохраняют interpreter-dependent или
uncaught behavior после исчерпания repair budget.

### Goal
Опубликовать один exact strict and bounded decoder decision для обеих
authorization field roles и выбрать clean replacement authorization identity
без runtime implementation.

### Scope
- Зафиксировать parser-owned numeric lexemes, strict constants, per-value и
  aggregate ceilings, accounting order и stable details.
- Зафиксировать source/inline field-role, identity, cardinality и semantic
  dispatch boundaries.
- Зафиксировать connected dual-environment RED/GREEN matrix и весь later
  implementation verification floor.
- Назвать replacement authorization id/path, exact source/reference objects,
  reciprocal relations, ceiling и protocol allowance.
- Не изменять runtime surface и не создавать replacement/successor cards.

### Acceptance
- Все card-level acceptance и stop conditions представлены normative delta
  scenarios и ordered decision-only tasks.
- Change apply-ready, содержит ровно одну modified capability и отделяет docs/
  spec verification от future implementation evidence.

### Depends On
- `investigate-type-safe-decoded-target-classification-boundary`

### Related
- `openspec/changes/decide-total-bounded-authorization-json-decoder-boundary/`

## Log
- 2026-08-24T07:08:33Z `$changerail-ff` создан после exhausted cycle-3 `R6` и
  Sol `xhigh` escalation; подготовлен один decision-only change без production,
  successor, runtime evidence, review или publish действий.
- 2026-08-24T07:18:11Z `$changerail-do` verified the frozen decision contract,
  synced exactly one `changerail-contracts` requirement, archived the change and
  moved this card to `3.inprogress` for fresh independent review. Runtime
  RED/GREEN is `not applicable`; no review, verdict, publish, commit or push was
  performed.
- 2026-08-24T07:32:02Z Bounded same-card rescue attempt 1 repaired cycle-1
  `NO-GO` R1 only: universal single-pass first-failure order and source/inline
  dual-environment collision rows now choose one exact detail. Existing `NO-GO`
  verdict was not replaced; ignored rescue manifest/evidence/preflight record
  the docs/spec checks. Runtime RED/GREEN remains `not applicable`.
- 2026-08-24T07:39:05Z Fresh independent cycle-2 `gpt-5.6-sol/high` review
  returned `GO`; all seven acceptance criteria passed and cycle-1 `NO-GO` R1
  remained preserved in ignored review history.
- 2026-08-24T08:38:06Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
