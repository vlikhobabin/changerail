## ADDED Requirements

### Requirement: Решение для total bounded authorization JSON decoder
ChangeRail MUST опубликовать tracked decision-only investigation до новой
authorization implementation после exhausted unpublished payload. Решение MUST
задать один strict, pair-preserving, total/non-throwing и resource-bounded JSON
decoder contract для source `Investigation authorization` values и inline
`Published investigation authorization` references, независимо от CPython
`PYTHONINTMAXSTRDIGITS`.

#### Scenario: Обе field roles используют один universal decoder
- **WHEN** preflight извлекает exact source либо inline authorization fields
- **THEN** он распознает только соответствующий case-sensitive one-line field,
  normalizes outer whitespace и не более одной enclosing backtick pair
- **AND** JSON в prose, code fences и иных fields не является candidate
- **AND** universal field-count, aggregate и per-value decode stage выполняется
  до role-specific cardinality, schema, identity, path и relation checks
- **AND** inline literal `none` остается `not-declared`, а все другие values
  проходят один и тот же decoder

#### Scenario: Numeric conversion принадлежит role validator
- **WHEN** strict scanner встречает RFC 8259 numeric token
- **THEN** он сохраняет token как parser-owned lexeme и не вызывает `int()`,
  `float()`, `Decimal()` или user-extensible numeric protocol во время decode
- **AND** maximum lexeme равен 64 ASCII characters, включая minus, fraction
  point и exponent marker/sign/digits
- **AND** 64-character lexeme проходит lexical stage, а 65-character lexeme
  получает detail `authorization JSON number exceeds 64 characters`
- **AND** только bounded integer-form ceiling может быть converted после role
  type validation, а fraction/exponent form не становится integer ceiling

#### Scenario: Strict constants имеют stable rejection
- **WHEN** source или inline value содержит `NaN`, `Infinity` либо `-Infinity`
- **THEN** authorization получает `invalid` с detail
  `authorization JSON must not contain NaN or Infinity`
- **AND** lowercase или malformed literal получает
  `authorization JSON must contain exactly one value`
- **AND** reject не вызывает semantic, review или model dispatch и не выпускает
  uncaught exception

#### Scenario: Number grammar и environment matrix детерминированы
- **WHEN** connected production matrix запускает `run_preflight` отдельно с
  `PYTHONINTMAXSTRDIGITS=640` и `PYTHONINTMAXSTRDIGITS=0`
- **THEN** positive/negative integer, fraction и exponent rows на 64/65
  characters имеют identical exact serialized results в обоих processes
- **AND** `0`, `-0`, signed negative, fractions и exponents проходят RFC 8259
  lexical grammar, тогда как `+1`, leading-zero forms, missing fraction/exponent
  digits, bare sign и trailing value получают exact syntax detail
- **AND** source ceiling `301..500` принимает только integer-form
  integer-not-boolean, а numeric identity values в обеих roles получают
  role-specific non-string detail до semantics

#### Scenario: Per-value budgets имеют exact boundaries
- **WHEN** decoder обрабатывает один normalized authorization value
- **THEN** он допускает максимум 4096 Unicode code points, 255 lexical tokens и
  nesting depth 16, где root container имеет depth один
- **AND** 4097 code points дают
  `authorization JSON value exceeds 4096 characters`, 257 tokens дают
  `authorization JSON value exceeds 255 tokens`, а depth 17 дает
  `authorization JSON value exceeds nesting depth 16`
- **AND** lexical tokens включают scalar tokens и `{`, `}`, `[`, `]`, `:`, `,`,
  whitespace не считается, а punctuation внутри strings не меняет counters
- **AND** exact 4096, 255 и depth 16 controls проходят universal limits

#### Scenario: Aggregate budgets предшествуют role cardinality
- **WHEN** один Markdown document содержит authorization fields одной role
- **THEN** universal stage допускает максимум 16 exact field values, 16384
  aggregate normalized code points и 1020 aggregate lexical tokens
- **AND** 17 fields дают `authorization fields exceed 16 values`, 16385 code
  points дают `authorization JSON aggregate exceeds 16384 characters`, а 1021
  tokens дают `authorization JSON aggregate exceeds 1020 tokens`
- **AND** exact aggregate limits проходят resource stage
- **AND** эти details одинаковы для source и inline roles; small duplicate
  inline fields только после universal stage получают role cardinality detail

#### Scenario: Universal first-failure order resolves every same-event collision
- **WHEN** universal extraction/scanner traverses exact fields in source order,
  normalized code points and lexical token events before role validation
- **THEN** it uses one pass with no fallback parser or rollback and applies this
  complete order: field count; aggregate characters; per-value characters;
  prohibited `NaN`/`Infinity`/`-Infinity`; generic RFC 8259 syntax; numeric
  lexeme length; nesting depth; per-value tokens; aggregate tokens
- **AND** the 17th field wins before its character/parser state; a same-code-point
  aggregate-character overrun wins over per-value characters and a token it
  would complete; and at one scanner position constant, syntax, numeric and
  depth rejects win in that stated order before token checks
- **AND** at one token per-value tokens win over aggregate tokens: after three
  255-token values, a valid 257-token fourth value fails on its 256th token with
  `authorization JSON value exceeds 255 tokens`, even though aggregate tokens
  would become 1021
- **AND** the future matrix has observable generated fixtures for field-count/
  aggregate-character, aggregate/per-value-character, character/token,
  constant/token, syntax/token, numeric/token, depth/token and per-value/
  aggregate-token collisions for source and inline roles under both
  `PYTHONINTMAXSTRDIGITS=640` and `PYTHONINTMAXSTRDIGITS=0`
- **AND** each four-run collision row has identical exact
  exit/outcome/status/detail/counters, no uncaught exception and zero semantic,
  review and model dispatch

#### Scenario: Pair-preserving role validators разделяют identity и semantics
- **WHEN** universal decoder успешно возвращает ordered decoded values
- **THEN** каждый object остается immutable ordered pairs, each number remains a
  numeric lexeme wrapper и unvalidated values не участвуют в hashing, mapping,
  path construction или relation lookup
- **AND** source role сохраняет published typed-hint, one-target, duplicate,
  six-field shape, identity, ceiling/allowance и exact-target order до semantics
- **AND** inline role требует ровно один object, reject-ит duplicate decoded keys,
  exact two-field shape и non-empty string `authorization_card`/
  `authorization_id` до mapping/path/tracked semantics
- **AND** inline role использует exact details
  `published authorization reference must contain exactly one value`,
  `published authorization reference contains duplicate decoded key: <key>`,
  `authorization reference must contain exactly authorization_card and authorization_id`
  и `authorization reference values must be non-empty strings`

#### Scenario: Decoder и structural rejects имеют zero-dispatch oracle
- **WHEN** extraction limit, aggregate limit, syntax, strict constant, numeric,
  depth/token/char, role cardinality, duplicate, shape или identity type check
  отклоняет value
- **THEN** preflight возвращает exit 1, outcome `investigation-required`,
  authorization `invalid`, exact detail, `llm_review.required: false` и reason
  `complexity guard requires investigation/simplification`
- **AND** `semantic_check_delta`, `semantic_review_dispatch_delta` и
  `model_launch_delta` равны zero, `uncaught_exception` равен false
- **AND** semantic relation reject запускается только после validated role
  mapping, может иметь `semantic_check_delta: 1`, но сохраняет zero review/model
  dispatch

#### Scenario: Connected future RED/GREEN matrix покрывает обе roles
- **WHEN** replacement authorization implementation готовится к review
- **THEN** каждый negative fixture начинается с fresh passing canonical base и
  одной mutation через production `run_preflight`
- **AND** matrix покрывает strict constants, numeric 64/65 and grammar rows,
  depth 16/17, tokens 255/257, chars 4096/4097, fields 16/17, aggregate
  chars/tokens exact/over, the complete ordered collision rows, source-versus-
  inline roles, duplicates, shape, identities, candidate cardinality и semantic
  relations
- **AND** оба environment runs имеют identical exact outcomes/details/counters,
  no uncaught exception и zero semantic/review/model dispatch на reject
- **AND** existing type-safe, phase-routed resume-integrity matrices, full smoke,
  release baseline, strict OpenSpec, source classification, Python compile,
  Ruff when available, public scan и diff/scope checks остаются mandatory

#### Scenario: Выбрана одна clean replacement authorization identity
- **WHEN** эта investigation опубликована и разрешено follow-up планирование
- **THEN** единственный следующий item —
  `authorize-total-bounded-phase-routed-resume-integrity-payload` с initial path
  `openspec/board/2.todo/authorize-total-bounded-phase-routed-resume-integrity-payload.md`
  и published path
  `openspec/board/4.done/authorize-total-bounded-phase-routed-resume-integrity-payload.md`
- **AND** он зависит от
  `investigate-total-bounded-authorization-json-decoder-boundary`, блокирует
  `replace-phase-routed-resume-integrity-boundary`, остается в ordinary 300
  added production LOC parser/smoke scope и не меняет schemas/runner/CLI/runtime
  docs
- **AND** failed `authorize-type-safe-phase-routed-resume-integrity-payload`
  остается forensic-only без repair, copy, publication или authority reuse

#### Scenario: Exact source и reference сохраняют downstream authority
- **WHEN** replacement authorization позднее опубликована
- **THEN** ее exact six-field object связывает published investigation
  `investigate-total-bounded-authorization-json-decoder-boundary` с
  `replace-phase-routed-resume-integrity-boundary` по exact `3.inprogress` path,
  production LOC ceiling 500 и protocol allowance true
- **AND** successor ссылается только на published
  `authorize-total-bounded-phase-routed-resume-integrity-payload` по exact
  `4.done` path/id
- **AND** investigation reciprocally blocks authorization и successor, а pilot
  wave не продолжается до publication successor

#### Scenario: Investigation и implementation verification разделены
- **WHEN** этот decision-only change доставляется и проверяется
- **THEN** его evidence ограничено strict card/OpenSpec validation, public scan,
  config parse, whitespace и scoped diff без production/runtime/successor edits
- **AND** runtime RED/GREEN evidence отмечается not applicable для decision
- **AND** dual-environment production matrix и полный implementation floor
  остаются mandatory future evidence и не считаются выполненными planning checks

#### Scenario: Fast-forward остается planning-only
- **WHEN** `$changerail-ff` завершает эту investigation
- **THEN** создаются только ее todo card и один active decision OpenSpec change
- **AND** main spec, archive, production parser, smoke/tests, schemas, runner,
  CLI, runtime docs, failed payload, successor и runtime verdict/evidence не
  изменяются и не создаются
