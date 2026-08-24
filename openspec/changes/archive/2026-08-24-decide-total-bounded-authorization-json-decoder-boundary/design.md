## Context

Published decision
`investigate-type-safe-decoded-target-classification-boundary` уже требует
pair-preserving decode, typed hints до target selection и запрет hashing/path/
relation use для unvalidated identity values. Failed unpublished successor
attempt добавил lexical length/nesting/comma guards, но оставил conversion
обычному CPython decoder. Поэтому syntactically valid 4301-digit integer
проходит ранние guards и зависит от process-wide `PYTHONINTMAXSTRDIGITS`.

Та же authority chain имеет вторую decoder entry point: inline
`Published investigation authorization` reference в successor card. Published
runtime читает его отдельным unrestricted `json.loads`; permissive constants и
deep values поэтому могут иметь другой outcome или выпустить `RecursionError`.
Две роли принадлежат одному trust boundary и не должны расходиться по syntax,
resource limits или exception behavior.

## Goals / Non-Goals

**Goals:**

- Определить один strict, total/non-throwing decoder primitive для обеих field
  roles.
- Исключить integer/float conversion из lexical decode и сделать numeric
  behavior независимым от interpreter process settings.
- Зафиксировать exact per-value и per-document aggregate budgets и stable
  details.
- Сохранить published pair-preserving/type-safe target classification после
  общего decode stage.
- Зафиксировать exact role cardinality, identity validation и semantic dispatch
  order.
- Подготовить connected dual-environment RED/GREEN contract и полный later
  implementation verification floor.
- Выбрать одну clean replacement authorization identity и exact lineage.

**Non-Goals:**

- Реализовывать decoder/parser/smoke или менять schemas, runner, CLI и runtime
  docs.
- Repair-ить, копировать, публиковать или архивировать failed payload.
- Создавать replacement authorization или downstream successor.
- Менять six-field source либо two-field reference wire shapes.
- Ослаблять exact tracked-HEAD/path/id/relation, LOC или protocol checks.
- Записывать runtime evidence/verdict, выполнять review, commit, push или
  publish в planning phase.

## Decisions

### 1. Один decoder принимает bounded sequence normalized field values

Общий primitive получает ordered sequence значений одной exact Markdown field
role. Extraction распознает только case-sensitive one-line list fields
`Investigation authorization` либо
`Published investigation authorization`; JSON в prose, code fences и других
fields игнорируется. Значение trim-ится по внешнему Markdown whitespace, затем
удаляется не более одной enclosing backtick pair. Universal budgets считаются
по полученной строке до role-specific cardinality/schema checks.

Inline literal `none` означает `not-declared` и не является JSON. Любое другое
значение обеих roles проходит один strict scanner/decoder. Source role передает
bounded sequence pair-preserved values published candidate selector. Inline
role после universal stage требует ровно один decoded object и exact
`authorization_card`/`authorization_id` shape.

Universal stage выполняется раньше role cardinality. Поэтому 17 exact fields в
любой role получают одинаковый aggregate decoder detail, а две small inline
fields получают поздний role detail
`published authorization reference must contain exactly one value`.

### 2. Numeric token является bounded lexeme, а не Python number

Scanner принимает только RFC 8259 number grammar:

```text
-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?
```

Каждый numeric lexeme ограничен 64 ASCII characters, включая optional minus,
decimal point, fraction digits, exponent marker/sign/digits. Lexeme 64
characters проходит lexical stage, 65 дает exact detail
`authorization JSON number exceeds 64 characters`. Scanner не вызывает
`int()`, `float()`, `Decimal()` или user-extensible numeric protocol.

После decode role validator классифицирует lexeme как integer-form либо
fraction/exponent-form. Только bounded integer-form может быть преобразован для
`production_loc_ceiling`; 64-character maximum находится ниже обоих required
process settings и conversion не зависит от них. Identity fields reject any
numeric wrapper как non-string. Fraction/exponent ceiling остается non-integer
даже если математическое значение равно целому.

Accepted lexical controls включают `0`, `-0`, `1`, `-1`, `1.0`, `-1.0`,
`1e0`, `1E+0`, `1e-0` и exact 64-character forms. `+1`, `01`, `-01`, `.1`,
`1.`, `1e`, bare `-` и trailing second value получают existing syntax detail
`authorization JSON must contain exactly one value`. Rows с 65-character
positive, negative, fraction и exponent lexemes получают numeric-limit detail.

### 3. Strict constants reject до schema и semantics

`NaN`, `Infinity` и `-Infinity` всегда дают
`authorization JSON must not contain NaN or Infinity`. Lowercase spellings и
иные malformed literals дают syntax detail. Parser не использует permissive
`parse_constant` defaults и не преобразует exponent forms в binary float, так
что finite/non-finite platform conversion не участвует в decode.

### 4. Per-value и aggregate budgets являются exact contract

Для каждого normalized value:

- maximum 4096 Unicode code points;
- maximum 255 lexical tokens;
- maximum nesting depth 16, где root container имеет depth 1;
- maximum 64 ASCII characters для каждого numeric lexeme.

Lexical token — каждый string, numeric либо literal token и каждый structural
token `{`, `}`, `[`, `]`, `:`, `,`. Whitespace не является token; punctuation
в string не считается structural token. Scanner не allocates pair/container
result до успешного scanner stage.

На один Markdown document и одну role extraction:

- maximum 16 exact field values;
- maximum 16384 normalized code points across all values;
- maximum 1020 lexical tokens across all values.

Для одного document universal traversal идет по exact extracted fields в их
source order, затем по normalized code points и scanner events каждого value.
Это один pass: scanner вычисляет candidate counter/state для текущего event,
выбирает первый applicable reject из нижнего fixed order и сразу прекращает
decode без second parser, fallback или rollback. Role cardinality/schema не
участвуют в этом order.

Universal first-failure order (ранний пункт всегда wins над поздним для одного
наблюдаемого field/code-point/token event):

1. admission очередного exact field: field count;
2. очередной normalized code point: aggregate characters, затем per-value
   characters;
3. тот же scanner position после successful character admission: exact
   prohibited `NaN`/`Infinity`/`-Infinity` constant, generic RFC 8259 syntax,
   numeric-lexeme length, nesting depth;
4. token emission: per-value tokens, затем aggregate tokens.

Поэтому 17th field wins над его character/parser state; на одном code point
aggregate-character detail wins над per-value-character detail и над token,
который этот code point мог бы завершить. На одном token prohibited constant
wins над generic syntax/token accounting, generic syntax wins над numeric/depth/
token accounting, numeric length wins над depth/token accounting, depth wins над
token accounting, а per-value token wins над aggregate token. Candidate counters
для rejected event не являются externally observable и не требуют commit.
Exact limits проходят; первый greater value отклоняется. Этот order стабилен
между roles, потому что role-specific checks начинаются только после universal
stage, и технически реализуем одним scanner state plus bounded field counters.

Stable details:

```text
authorization JSON value exceeds 4096 characters
authorization JSON value exceeds 255 tokens
authorization JSON value exceeds nesting depth 16
authorization JSON number exceeds 64 characters
authorization fields exceed 16 values
authorization JSON aggregate exceeds 16384 characters
authorization JSON aggregate exceeds 1020 tokens
authorization JSON must not contain NaN or Infinity
authorization JSON must contain exactly one value
```

### 5. Collision rows фиксируют same-event detail

Future matrix строит каждый row из fresh passing canonical base и одной
constructible mutation. Для **каждого** row ниже harness запускает source и
inline field variants отдельно при `PYTHONINTMAXSTRDIGITS=640` и `0`; все четыре
результата обязаны иметь identical exact outcome/status/detail/counters и zero
semantic/review/model dispatch.

| Collision mutation | Same event | Required detail |
| --- | --- | --- |
| 17th exact role field also makes its normalized value cross aggregate chars | field admission | `authorization fields exceed 16 values` |
| prior aggregate is 12288 chars and next value reaches its 4097th char (aggregate 16385) | same code point | `authorization JSON aggregate exceeds 16384 characters` |
| a code point would both cross aggregate chars and complete a token | same code point | `authorization JSON aggregate exceeds 16384 characters` |
| a `NaN`, `Infinity` or `-Infinity` candidate arrives when aggregate tokens would exceed 1020 | same scanner position | `authorization JSON must not contain NaN or Infinity` |
| malformed trailing value arrives when its candidate token would exceed a token budget | same scanner position | `authorization JSON must contain exactly one value` |
| a 65th numeric-lexeme character would also emit an over-budget token | same scanner position | `authorization JSON number exceeds 64 characters` |
| opening depth 17 would also emit an over-budget token | same scanner position | `authorization JSON value exceeds nesting depth 16` |
| three preceding values consume 255 tokens each; valid 257-token fourth value reaches per-value 256 and aggregate 1021 on its 256th token | same token | `authorization JSON value exceeds 255 tokens` |

The last row is the reviewer collision: aggregate-token accounting remains
required, but per-value token is the earlier token-stage check. Fixtures use
generated bounded JSON to establish the stated scanner state rather than relying
on parser implementation accidents.

### 6. Role validation использует pairs и typed identities

Общий decoder возвращает immutable ordered pairs для каждого object и numeric
lexeme wrapper для каждого number. Он не материализует object mapping и не
hash-ит decoded keys/values.

Source role сохраняет published order: target selection по trusted typed string
hints, ровно один current target, duplicate decoded keys, six-field shape,
четыре non-empty string identities, bounded integer-form ceiling `301..500`,
boolean protocol allowance, exact identity equality и только затем mapping/path/
tracked/relation semantics. Existing exact source details сохраняются.

Inline role проверяет duplicate decoded keys, exact two-field shape и non-empty
string `authorization_card`/`authorization_id` до mapping/path/read/tracked
semantics. Exact inline details:

```text
published authorization reference must contain exactly one value
published authorization reference contains duplicate decoded key: <key>
authorization reference must contain exactly authorization_card and authorization_id
authorization reference values must be non-empty strings
```

Обе роли используют одинаковые universal decoder details. Structural/resource/
type reject возвращает authorization `invalid`, exit 1, outcome
`investigation-required`, `llm_review.required: false`, reason
`complexity guard requires investigation/simplification`, zero
`semantic_check_delta`, `semantic_review_dispatch_delta`, `model_launch_delta`
и `uncaught_exception: false`. Semantic relation checks начинаются только после
role mapping и на своем reject имеют `semantic_check_delta: 1`, но zero review/
model dispatch.

### 7. Connected matrix доказывает environment и role parity

Каждая negative row начинается с fresh passing canonical fixture и одной
mutation. Одна и та же production `run_preflight` matrix выполняется отдельными
connected processes при `PYTHONINTMAXSTRDIGITS=640` и
`PYTHONINTMAXSTRDIGITS=0`; harness сравнивает exact serialized
exit/outcome/status/detail/reason/counters/exception results между процессами.

Matrix включает обе roles и следующие groups:

- strict `NaN`, `Infinity`, `-Infinity`, lowercase/malformed literals;
- numeric 64/65 characters для positive/negative integer, fraction и exponent;
- valid/malformed signs, leading zero, fraction и exponent grammar;
- source ceiling integer-form `300`, `301`, `500`, `501`, booleans и
  fraction/exponent forms; numeric values во всех identity fields обеих roles;
- value chars 4096/4097, tokens 255/257 и depth 16/17, включая braces/commas in
  strings as non-structural controls;
- field count 16/17, aggregate chars 16384/16385 и aggregate tokens 1020/1021;
- every ordered first-failure collision from section 5, including the three
  255-token values plus the fourth valid 257-token value where token 256 is
  both per-value 256 and aggregate 1021;
- exact same universal mutations in source and inline fields, plus role-specific
  zero/one/multiple cardinality, duplicate, shape and identity rows;
- existing type-safe candidate/duplicate/order/relation matrix и existing
  phase-routed resume-integrity matrix.

Counters instrument production semantic/review dispatch boundaries; constant
stubs или inference только из `llm_review.required` не являются evidence.
Reject matrix не запускает model.

### 8. Выбрана clean replacement authorization lineage

Единственный следующий authorization work item после publication этой
investigation:

- id: `authorize-total-bounded-phase-routed-resume-integrity-payload`;
- initial path:
  `openspec/board/2.todo/authorize-total-bounded-phase-routed-resume-integrity-payload.md`;
- published path:
  `openspec/board/4.done/authorize-total-bounded-phase-routed-resume-integrity-payload.md`.

Он `Depends On` `investigate-total-bounded-authorization-json-decoder-boundary`
и `Blocks` `replace-phase-routed-resume-integrity-boundary`. Current
investigation reciprocally blocks оба. Later implementation ограничен owning
parser, connected smoke и its card/change/spec artifacts, ordinary hard ceiling
300 added production LOC; schemas, runner, CLI и runtime docs остаются вне
scope.

Future published source содержит ровно один object:

```json
{"investigation_card":"openspec/board/4.done/investigate-total-bounded-authorization-json-decoder-boundary.md","investigation_id":"investigate-total-bounded-authorization-json-decoder-boundary","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Future successor reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-total-bounded-phase-routed-resume-integrity-payload.md","authorization_id":"authorize-total-bounded-phase-routed-resume-integrity-payload"}
```

Failed `authorize-type-safe-phase-routed-resume-integrity-payload` остается
forensic-only. Его card/change/code/test payload не repair-ится, не копируется и
не используется как tracked authority.

### 8. Investigation verification не подменяет implementation evidence

Decision delivery проверяет только card/OpenSpec consistency, strict validation,
public safety, whitespace и scoped absence production/runtime/successor edits.
RED/GREEN runtime evidence неприменима к decision-only payload.

Later implementation отдельно обязана выполнить dual-environment production
matrix, existing phase-routed matrix, full review-preflight smoke, release
baseline, source-classification check, strict OpenSpec, Python compile, Ruff
when available, public scan и diff/scope checks. Ни одна planning validation не
засчитывается вместо этих runtime checks.

## Risks / Trade-offs

- [Risk] 64-character numbers уже, чем arbitrary precision JSON. -> Mitigation:
  authorization shapes используют только ceiling `301..500`; unrelated huge
  numbers не имеют business value внутри bounded authority channel.
- [Risk] 4096/255/16 per-value limits отклоняют unusually large unrelated JSON
  examples. -> Mitigation: decoder читает только exact authorization fields;
  public card prose вне fields не затрагивается.
- [Risk] Exact details становятся compatibility contract. -> Mitigation: они
  нужны для deterministic fail-closed review and may change only through a new
  decision/spec delta.
- [Risk] Один decoder повышает coupling двух roles. -> Mitigation: shared lexical
  trust boundary и separate role validators сохраняют ясную ownership границу.

## Migration Plan

1. Deliver этот decision-only change, sync один `changerail-contracts`
   requirement, archive и получить fresh independent `GO` перед publish.
2. После publication создать только
   `authorize-total-bounded-phase-routed-resume-integrity-payload`; failed
   payload не переносить.
3. Implement shared decoder и connected dual-environment matrix, выполнить весь
   later verification floor, independent review и publish replacement source.
4. Только затем создать `replace-phase-routed-resume-integrity-boundary` с exact
   two-field reference, ceiling 500 и protocol allowance true.
5. Не продолжать pilot wave до publication downstream successor.

Rollback investigation является docs/spec rollback. Любой later parser rollback
должен одновременно revoke replacement source до publication зависимого
successor.

## Open Questions

- none
