# Исследовать incremental authorization gate boundary

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
- Published decision
  `openspec/board/4.done/investigate-total-bounded-authorization-json-decoder-boundary.md`,
  commit `6e1cbfa07884b71f5cefa678de8a2a0401a8392f`.
- Неопубликованный payload
  `authorize-total-bounded-phase-routed-resume-integrity-payload` получил
  independent cycle 1 `NO-GO` с blockers `R1`-`R3`, затем cycle 2 `NO-GO` с
  blockers `R1`-`R2`; same-card rescue budget исчерпан `1/1`.
- Cycle 2 reviewed fingerprint:
  `sha256:95f79ea4d67a7b7e570b1a94062f6a0079d56218f80426fad1701e3017d8cc7d`.

## Summary
Опубликовать decision-only investigation, которая сохраняет все limits,
details и first-failure order решения `6e1cbfa`, но выбирает incremental
extraction/scanner boundary, необходимую после двух независимых `NO-GO`.
Решение немедленно отклоняет exact поле 17 до доступа к его line end или
content и распознает RFC 8259 number конечным автоматом по одному character,
чтобы 4301-digit integer стабильно падал на numeric character 65, а не на
value character 4097.

Исчерпанный payload остается forensic-only и не может быть repaired,
reviewed повторно или published. Эта investigation публично supersede-ит
выбранную `6e1cbfa` exclusive identity без переписывания published decision,
card, archive, review history или dirty payload и выбирает чистую lineage:

`investigate-incremental-authorization-gate-boundary` ->
`authorize-bounded-incremental-authorization-gate-payload` ->
`implement-incremental-authorization-gate-boundary` ->
`authorize-incremental-bounded-phase-routed-resume-integrity-payload` ->
`replace-phase-routed-resume-integrity-boundary`.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Decision-only scope не создает authority. Обе authorization identities B и D
могут появиться только как отдельные будущие опубликованные карточки в exact
lineage ниже.

## Depends On
- `investigate-total-bounded-authorization-json-decoder-boundary`

## Blocks
- `authorize-bounded-incremental-authorization-gate-payload`

## Decision Contract
- Все published ceilings сохраняются exact: numeric lexeme 64 ASCII
  characters; normalized value 4096 Unicode code points, 255 lexical tokens и
  depth 16; один role extraction одного Markdown document содержит не более 16
  exact fields, 16384 aggregate code points и 1020 aggregate tokens.
- Все published stable details сохраняются без изменений:
  `authorization JSON must not contain NaN or Infinity`,
  `authorization JSON must contain exactly one value`,
  `authorization JSON number exceeds 64 characters`,
  `authorization JSON value exceeds 4096 characters`,
  `authorization JSON value exceeds 255 tokens`,
  `authorization JSON value exceeds nesting depth 16`,
  `authorization fields exceed 16 values`,
  `authorization JSON aggregate exceeds 16384 characters` и
  `authorization JSON aggregate exceeds 1020 tokens`.
- Universal first-failure order остается exact: field count; aggregate
  characters; per-value characters; prohibited exact constants; generic RFC
  8259 syntax; numeric lexeme length; nesting depth; per-value tokens;
  aggregate tokens. Earlier gate wins на одном prefix/character/scanner/token
  event; scanner немедленно останавливается без fallback или rollback.
- Exact-field extractor распознает field prefix по offsets исходного document,
  без `splitlines()` и без поиска line terminator заранее. Как только prefix
  подтверждает 17th exact field данной role, он возвращает field-count detail
  до чтения первого value character, поиска line end, trim/backtick access или
  сохранения span.
- Number scanner является incremental RFC 8259 FSM для sign, integer,
  fraction и exponent. Он не применяет regex к оставшемуся value и на каждом
  admitted character выполняет published character gates, syntax transition и
  numeric-length gate. Valid numeric continuation 65 получает numeric detail
  на character 65; поэтому 4301-digit integer не достигает character 4097.
- Ни universal decoder, ни role validators не вызывают `int()`, `float()`,
  `Decimal()` или user-extensible numeric conversion. Ceiling проверяется над
  integer-form numeric lexeme exact decimal length/lexicographic comparison и
  сохраняется как bounded immutable lexeme до semantic authority comparison.
- Prohibited constants распознаются exact на любой nesting depth только с
  JSON token delimiter: end of normalized value, RFC 8259 whitespace, comma,
  `]` или `}`. Scanner не поглощает delimiter до constant reject. `NaNx`,
  `Infinityx`, `-Infinityx`, lowercase или malformed literal получают generic
  syntax detail; exact nested constant получает constant detail до token
  gates. Только exact lowercase inline literal `none` вне JSON остается
  `not-declared`; `NONE` и `None` проходят strict decode и отклоняются.
- Сохраняются published pair preservation, source/inline universal-first role
  ordering, cardinality, duplicate, shape, identity и semantic boundaries.
  Unvalidated values не участвуют в hashing, mapping, path или relation lookup.
- Connected matrix запускает source и inline rows отдельными processes при
  `PYTHONINTMAXSTRDIGITS=640` и `0`; каждая negative row начинается с fresh
  passing base и одной mutation. Она включает exact 4301-digit rows и
  read-bound oracle поля 17, все published boundaries/collisions, exact nested
  constant delimiters и identical exact exit/outcome/status/detail/counters.
- Decoder/structural reject сохраняет exit 1, outcome
  `investigation-required`, authorization `invalid`, exact detail,
  `llm_review.required: false`, reason `complexity guard requires
  investigation/simplification`, zero semantic/review/model dispatch и
  `uncaught_exception: false`.

## Clean Lineage
- A, эта investigation, публикует только decision и supersession record.
- B, `authorize-bounded-incremental-authorization-gate-payload`, зависит от A
  и блокирует C. Его единственный exact six-field object:
  `{"investigation_card":"openspec/board/4.done/investigate-incremental-authorization-gate-boundary.md","investigation_id":"investigate-incremental-authorization-gate-boundary","successor_card":"openspec/board/3.inprogress/implement-incremental-authorization-gate-boundary.md","successor_id":"implement-incremental-authorization-gate-boundary","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`.
- C, `implement-incremental-authorization-gate-boundary`, зависит только от
  published B exact reference
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-incremental-authorization-gate-payload.md","authorization_id":"authorize-bounded-incremental-authorization-gate-payload"}`,
  реализует incremental extraction/FSM и блокирует D. C не наследует и не
  ссылается на superseded payload identity.
- D, `authorize-incremental-bounded-phase-routed-resume-integrity-payload`,
  зависит от published C и блокирует exact existing successor. Его единственный
  exact six-field object:
  `{"investigation_card":"openspec/board/4.done/investigate-incremental-authorization-gate-boundary.md","investigation_id":"investigate-incremental-authorization-gate-boundary","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
- Existing `replace-phase-routed-resume-integrity-boundary` позднее зависит
  только от published D exact reference
  `{"authorization_card":"openspec/board/4.done/authorize-incremental-bounded-phase-routed-resume-integrity-payload.md","authorization_id":"authorize-incremental-bounded-phase-routed-resume-integrity-payload"}`.
  B не authorizes existing successor, а D не authorizes C.
- Неопубликованный `authorize-total-bounded-phase-routed-resume-integrity-payload`
  получает status `SUPERSEDED` только как conclusion этой новой published
  decision. Его tracked/ignored history не изменяется, он никогда не становится
  `4.done` source и ни одна новая карточка не использует его id/path как
  authorization reference.

## Acceptance
- Card и один active change полностью сохраняют limits, details, accounting,
  first-failure order, dual-role behavior и zero-dispatch oracle `6e1cbfa`.
- Exact 17th-field gate наблюдаем до line-end/content access для source и inline
  roles, а incremental RFC 8259 FSM наблюдаемо отклоняет 65th numeric character
  до любого scan/read character 4097.
- Exact nested constant delimiter rows различают end/whitespace/comma/`]`/`}`
  от suffix/malformed literals на каждой nesting form.
- Connected rows включают 4301 digits, обе roles и оба
  `PYTHONINTMAXSTRDIGITS` environments с identical results и no conversion,
  exception или semantic/review/model dispatch.
- Exhausted payload признан non-repairable/non-publishable и superseded без
  изменения его worktree, history, archived artifacts или published `6e1cbfa`.
- Exact A->B->C->D->successor relations, ids, paths, B ceiling 301/protocol
  false и D ceiling 500/protocol true совпадают во всех artifacts.
- Planning изменяет только эту todo card и один decision change. Code, tests,
  main specs, archive, verdict/evidence/runtime state и successor cards не
  создаются и не меняются.

## Non-Goals
- Repair, copy, re-review, publish или mutation исчерпанного payload/worktree.
- Изменение production parser, smoke/tests, schemas, runner, CLI/runtime docs
  или main spec во время fast-forward.
- Создание B, C, D или изменение existing successor.
- Sync/archive, verdict, commit, push или publish в planning phase.

## Stop Conditions
- Остановить delivery при изменении любого limit/detail/order из `6e1cbfa`.
- Остановить C, если B не опубликована exact с ceiling 301/protocol false.
- Остановить D, если C не опубликована; остановить successor, если D не
  опубликована exact с ceiling 500/protocol true.
- Остановить implementation при чтении content поля 17, whole-lexeme numeric
  match, numeric conversion, различии environments или отсутствии 4301 rows.
- Остановить decision change, если нужен code/test/main-spec/archive/verdict
  edit до `$changerail-do`.

## Change Set
- `decide-incremental-authorization-gate-boundary`

## Verify
### Investigation planning/delivery
- `bin/openspec validate decide-incremental-authorization-gate-boundary --strict`.
- После later apply-time sync: `bin/openspec validate changerail-contracts
  --strict` и `bin/openspec validate --all --strict`.
- `python3 scripts/public-surface-scan.py`, JSON parse `.mcp.json`, TOML parse
  `.codex/config.toml`, `git diff --check`, explicit untracked whitespace scan
  и scoped status/diff.
- Runtime RED/GREEN: `not applicable` для decision-only payload.

### Later implementation
- Connected production `run_preflight` matrix в отдельных processes при
  `PYTHONINTMAXSTRDIGITS=640` и `0`, включая both-role 4301-digit и field-17
  read-bound rows, nested constants и все `6e1cbfa` rows.
- Existing phase-routed resume-integrity matrix, полный
  `python3 scripts/smoke-review-preflight.py`, release baseline, source
  classification, strict OpenSpec, Python compile, Ruff when available, public
  scan, whitespace и scoped diff checks.

## Archive
- `openspec/changes/archive/2026-08-24-decide-incremental-authorization-gate-boundary/`

## Related
- `openspec/board/4.done/investigate-total-bounded-authorization-json-decoder-boundary.md`
- `openspec/changes/archive/2026-08-24-decide-total-bounded-authorization-json-decoder-boundary/`
- `openspec/changes/archive/2026-08-24-decide-incremental-authorization-gate-boundary/`

## Result
Decision-only investigation verified, synced as exactly one
`changerail-contracts` requirement and archived. The published `6e1cbfa`
limits, details and universal first-failure order, the cycle-2 forensic
`NO-GO` R1/R2 findings and fingerprint, and the exact A->B->C->D->successor
lineage were checked without modifying the forensic payload or history.
`bin/openspec validate --all --strict`, current and reachable-history public
surface scans, JSON/TOML parsing, whitespace/scope checks and the 36/36 release
baseline passed with retained ignored evidence.
Production parser, tests, schemas, runner, CLI/runtime docs, B/C/D, the
existing successor, verdict, commit, push and publish remain unchanged or
absent. Runtime RED/GREEN is `not applicable` for this decision-only payload.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-incremental-authorization-gate-boundary`

### Why
Exhausted implementation не соблюдает published earliest gates: field 17
сканируется до rejection, а 4301-digit integer проходит greedy match и падает
на character 4097 вместо numeric character 65.

### Goal
Опубликовать exact incremental boundary и clean superseding lineage без runtime
implementation или изменения forensic history.

### Scope
- Сохранить весь bounded decoder contract `6e1cbfa`.
- Добавить exact field-prefix admission, incremental numeric FSM, constant
  delimiter и no-conversion decisions с connected future oracles.
- Зафиксировать supersession и exact A->B->C->D->successor lineage.
- Не создавать downstream cards и не менять runtime/main/archive surface.

### Acceptance
- Все card acceptance и stop conditions представлены normative scenarios и
  ordered decision-only tasks.
- Change apply-ready и содержит ровно одну modified capability.

### Depends On
- `investigate-total-bounded-authorization-json-decoder-boundary`

### Related
- `openspec/changes/decide-incremental-authorization-gate-boundary/`

## Log
- 2026-08-24T14:20:00Z `$changerail-ff` создан из published base `6e1cbfa` и
  forensic cycle-1/cycle-2 `NO-GO` history; подготовлен один decision-only
  change без implementation, main-spec, archive, verdict, commit или publish.
- 2026-08-24T15:48:00Z `$changerail-do` сверил decision contract и forensic
  cycle-2 `NO-GO` R1/R2 fingerprint, синхронизировал ровно один
  `changerail-contracts` requirement, архивировал только decision change и
  передал A в `3.inprogress` для fresh independent review. Strict OpenSpec,
  current/history public surface, JSON/TOML, whitespace/scope и 36/36 release
  baseline passed; runtime RED/GREEN `not applicable`. Code/tests/schemas/
  runner/CLI/runtime docs, B/C/D, successor, verdict, commit, push и publish
  не создавались и не менялись.
- 2026-08-24T16:26:09Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
