## Context

Published decision `6e1cbfa` выбрала один strict, total/non-throwing и bounded
decoder для source `Investigation authorization` и inline
`Published investigation authorization`. Она установила правильные ceilings,
stable details, pair-preserving role boundary и first-failure order, а также
выбрала exclusive implementation identity
`authorize-total-bounded-phase-routed-resume-integrity-payload`.

Эта identity осталась неопубликованной. Independent cycle 1 нашел unbounded
field extraction, неточные special literals и неполный connected oracle.
Same-card repair закрыл literal/oracle части, но cycle 2 доказал два оставшихся
blocker-а: extractor ищет конец и trim-ит content поля 17 до admission gate, а
numeric regex полностью матчится до length admission, из-за чего 4301-digit
integer получает value-character detail на 4097 вместо numeric detail на 65.
Rescue budget `1/1` исчерпан. Dirty payload не является source для новой работы.

Decision затрагивает только ChangeRail-owned `changerail-contracts` capability.
Planning создает card и artifacts; production surface
`scripts/changerail_review_preflight.py` и connected smoke будут затронуты
только будущей отдельной implementation card C.

## Goals / Non-Goals

**Goals:**

- Сохранить без ослабления все limits, details и ordering `6e1cbfa`.
- Выбрать incremental exact-field admission и RFC 8259 numeric FSM, которые
  делают два cycle-2 blocker-а наблюдаемыми и исправимыми в clean payload.
- Запретить numeric conversion и точно определить nested constant delimiters.
- Записать неизменяемый supersession outcome и linear A->B->C->D->successor
  lineage с exact ids, paths, relations и authorization objects.
- Отделить decision verification от будущего connected runtime evidence.

**Non-Goals:**

- Исправлять, копировать, re-review-ить или публиковать исчерпанный payload.
- Менять parser, tests, schemas, runner, CLI/runtime docs или main spec во время
  fast-forward.
- Создавать B, C, D или редактировать existing successor.
- Архивировать, писать verdict, commit/push или публиковать planning payload.

## Decisions

### 1. `6e1cbfa` остается normative lower boundary

Новый decision является additive refinement, а не replacement текста
published history. Он сохраняет numeric 64; per-value 4096 chars/255 tokens/
depth 16; aggregate 16 fields/16384 chars/1020 tokens; все exact details;
source/inline universal-first validation; immutable pairs; stable zero-dispatch
outcome. First-failure order остается:

1. field count;
2. aggregate characters;
3. per-value characters;
4. prohibited exact constants;
5. generic RFC 8259 syntax;
6. numeric lexeme length;
7. nesting depth;
8. per-value tokens;
9. aggregate tokens.

Alternative: изменить precedence так, чтобы numeric всегда предшествовал
character budgets. Это отвергнуто: оно переписало бы published collision
contract. Incremental FSM нужен для раннего numeric reject внутри прежнего
order, а не для нового order.

### 2. Field admission происходит на exact prefix

Extractor проходит offsets исходного Markdown document и распознает
case-sensitive one-line field prefix. Он не вызывает `splitlines()` и не ищет
newline до admission. После распознавания prefix увеличивается role-local field
counter. Для значения 17 немедленно возвращается
`authorization fields exceed 16 values`: до чтения первого value character,
line-end search, outer whitespace/backtick normalization или span retention.

Первые 16 admitted fields сохраняются как bounded offsets/spans; затем каждый
value проходит обычные aggregate/per-value/scanner gates. JSON в prose, fenced
blocks и других fields не является candidate по прежним extraction rules.

Alternative: bounded spans после генератора, использующего line search. Это
отвергнуто cycle 2: bounded storage не доказывает no-read-before-gate.

### 3. Number является incremental RFC 8259 FSM

FSM различает states `minus`, `zero`, `integer`, `fraction-dot`,
`fraction-digits`, `exponent-marker`, `exponent-sign`, `exponent-digits` и
`complete`. На каждом новом code point сначала применяются aggregate и
per-value character gates, затем syntax transition, затем при valid numeric
continuation увеличивается numeric length и применяется limit 64. Whole-tail
regex, fallback parser и rollback запрещены.

На valid digit 65 FSM возвращает
`authorization JSON number exceeds 64 characters` немедленно. Поэтому source и
inline 4301-digit integers в обоих environments завершаются на numeric
character 65 и никогда не читают/сканируют character 4097. Invalid continuation
на позиции 65 является syntax, а не numeric overrun; exact 64-character number
проходит только при legal delimiter.

Authorization decoder и role validators не используют `int()`, `float()`,
`Decimal()` или user-extensible numeric protocol. Integer-form ceiling
проверяется по canonical decimal sign/digits, length и lexicographic comparison
с string bounds. Boolean, negative, fraction/exponent и out-of-range lexemes
сохраняют published role-specific type/range ordering.

Alternative: regex с `{1,65}` и post-match length. Это отвергнуто: regex может
читать за earliest gate и плохо доказывает exact read boundary. Alternative:
`int()` после 64-character bound. Это безопаснее старого payload, но отвергнуто
как ненужная зависимость authority channel от interpreter conversion.

### 4. Prohibited constants требуют exact delimiter

`NaN`, `Infinity` и `-Infinity` являются prohibited constant только когда
следующий event есть end of normalized value, RFC 8259 whitespace, comma, `]`
или `}`. Правило одинаково на root и любой nesting depth. Scanner допускает
один bounded lookahead event: delimiter проходит character budgets, но не
поглощается и не учитывается как token до constant reject. На end reject
возникает при EOF event.

Suffix character переводит candidate в generic syntax path: `NaNx`,
`Infinityx`, `-Infinityx`, lowercase и malformed variants получают
`authorization JSON must contain exactly one value`. Exact nested constant
получает constant detail раньше depth/token gates на том же scanner position.
Inline sentinel применяется отдельно и только к normalized literal `none`;
`NONE`/`None` входят в strict decoder.

Alternative: prefix matching prohibited constant. Оно отвергнуто cycle 1,
потому что меняет stable detail для malformed JSON.

### 5. Connected oracle проверяет read boundary, не только detail

Future matrix запускает production `run_preflight` отдельно при
`PYTHONINTMAXSTRDIGITS=640` и `0`. Для обеих roles она сохраняет published rows
для constants, grammar, 64/65, 4096/4097, 255/257, depth 16/17, fields 16/17,
aggregate exact/over, all same-event collisions, cardinality/duplicate/shape/
identity/semantics и existing phase-routed behavior.

К ним добавляются:

- instrumented field-17 rows, где любое line-end/content access после exact
  prefix делает oracle fail;
- 4301-digit rows с expected numeric detail/event 65 и forbidden read/scan
  event 4097;
- nested constant rows для каждого exact delimiter и suffix/malformed controls;
- no-conversion instrumentation для decoder и role validation.

Каждый negative начинается с fresh passing base и одной mutation. Four-run
observation source/inline x 640/0 сравнивает exact exit, outcome, authorization
status/detail, reason, counters, exception и dispatch deltas.

### 6. Supersession сохраняет историю и разделяет две authority roles

Published `6e1cbfa`, exhausted worktree, archived artifacts и ignored cycle
history не изменяются. Новая investigation после publication является
единственным tracked source утверждения, что unpublished exclusive identity
`authorize-total-bounded-phase-routed-resume-integrity-payload` имеет outcome
`SUPERSEDED`, не может стать `4.done` authority и не должна упоминаться в новых
authorization references.

Чистая lineage содержит только следующие dependency/block edges:

- A зависит от published `investigate-total-bounded-authorization-json-decoder-boundary`
  и блокирует B;
- B зависит от published A и блокирует C;
- C зависит от published B exact reference и блокирует D;
- D зависит от published C и блокирует existing successor;
- successor зависит от published D exact reference.

B materializes exact source для bounded implementation C:

```json
{"investigation_card":"openspec/board/4.done/investigate-incremental-authorization-gate-boundary.md","investigation_id":"investigate-incremental-authorization-gate-boundary","successor_card":"openspec/board/3.inprogress/implement-incremental-authorization-gate-boundary.md","successor_id":"implement-incremental-authorization-gate-boundary","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

D materializes отдельный exact source для existing successor:

```json
{"investigation_card":"openspec/board/4.done/investigate-incremental-authorization-gate-boundary.md","investigation_id":"investigate-incremental-authorization-gate-boundary","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

B не authorizes existing successor; D не authorizes C. C использует only exact
published B reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-incremental-authorization-gate-payload.md","authorization_id":"authorize-bounded-incremental-authorization-gate-payload"}
```

Existing successor использует only exact published D reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-incremental-bounded-phase-routed-resume-integrity-payload.md","authorization_id":"authorize-incremental-bounded-phase-routed-resume-integrity-payload"}
```

Так authority для 301-line incremental implementation не дает protocol
allowance, а 500-line downstream payload получает allowance только после C.

## Risks / Trade-offs

- [Risk] Ceiling 301 разрешает на одну production line больше ordinary limit. ->
  Mitigation: B является отдельным clean published authorization, protocol
  allowance false и exact target ограничен C.
- [Risk] Incremental FSM сложнее library decoder. -> Mitigation: finite states,
  exact event order и connected dual-environment oracle делают boundary
  обозримой; второй production path запрещен.
- [Risk] String range comparison может быть реализована неточно. -> Mitigation:
  canonical RFC 8259 integer-form grammar, explicit sign/zero rules и exact
  boundary rows для 301/500.
- [Risk] Supersession может выглядеть как history rewrite. -> Mitigation:
  старые tracked/runtime artifacts остаются неизменными; новый decision только
  добавляет более поздний authoritative outcome.
- [Risk] One-character constant lookahead влияет на accounting. -> Mitigation:
  delimiter проходит character gates, но constant detail выигрывает до
  delimiter token/depth processing по published precedence.

## Migration Plan

1. Deliver decision-only A, sync один `changerail-contracts` requirement,
   archive и получить fresh independent `GO`/publish.
2. Создать и publish B exact с ceiling 301/protocol false; не создавать C до B.
3. Создать C с reference только на published B, реализовать incremental gate и
   весь connected matrix, review/publish.
4. Создать и publish D exact с ceiling 500/protocol true только после C.
5. Existing successor может продолжиться только с reference на published D.

Rollback A до downstream publication является docs/spec rollback. После
publication B/C/D rollback обязан fail-closed revoke соответствующую source
раньше зависимого successor; superseded payload не возвращается в lineage.

## Open Questions

- none
