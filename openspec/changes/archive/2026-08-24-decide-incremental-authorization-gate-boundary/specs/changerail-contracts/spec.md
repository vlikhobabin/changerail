## ADDED Requirements

### Requirement: Решение для incremental authorization gate boundary
ChangeRail MUST опубликовать tracked decision-only investigation после
исчерпания unpublished total-bounded payload. Решение MUST сохранить exact
limits, details и universal order published commit `6e1cbfa`, MUST выбрать
incremental field/numeric admission и MUST определить clean superseding
authorization lineage без изменения forensic history.

#### Scenario: Published bounded contract сохраняется полностью
- **WHEN** incremental investigation определяет новый implementation boundary
- **THEN** numeric lexeme limit остается 64 ASCII characters вместе со знаком,
  fraction point и exponent marker/sign/digits
- **AND** normalized value limits остаются 4096 Unicode code points, 255 lexical
  tokens и nesting depth 16 с root container depth one
- **AND** role extraction одного Markdown document остается ограничен 16 exact
  fields, 16384 aggregate normalized code points и 1020 aggregate tokens
- **AND** lexical tokens по-прежнему включают scalar tokens и `{`, `}`, `[`,
  `]`, `:`, `,`, не включают whitespace и не считают punctuation inside string
- **AND** exact-limit controls проходят universal stage, а over-limit inputs
  получают опубликованные stable details

#### Scenario: Universal first-failure order не изменяется
- **WHEN** extractor/scanner проходит exact fields в source order по normalized
  character и lexical token events до role validation
- **THEN** complete order остается field count; aggregate characters; per-value
  characters; prohibited exact constants; generic RFC 8259 syntax; numeric
  lexeme length; nesting depth; per-value tokens; aggregate tokens
- **AND** earlier gate wins на одном prefix/character/scanner/token event и
  scanner останавливается без fallback или rollback
- **AND** 17th field wins before content, aggregate character wins over
  per-value character/token, constant/syntax/numeric/depth win в указанном
  порядке before token gates, а per-value token wins over aggregate token
- **AND** после трех 255-token values valid fourth 257-token value получает
  `authorization JSON value exceeds 255 tokens` на token 256, хотя aggregate
  достигает 1021
- **AND** connected collision rows явно покрывают field-count/aggregate-char,
  aggregate/per-value-char, character/token, constant/token, syntax/token,
  numeric/token, depth/token и per-value/aggregate-token ties
- **AND** все details остаются exact:
  `authorization JSON must not contain NaN or Infinity`,
  `authorization JSON must contain exactly one value`,
  `authorization JSON number exceeds 64 characters`,
  `authorization JSON value exceeds 4096 characters`,
  `authorization JSON value exceeds 255 tokens`,
  `authorization JSON value exceeds nesting depth 16`,
  `authorization fields exceed 16 values`,
  `authorization JSON aggregate exceeds 16384 characters` и
  `authorization JSON aggregate exceeds 1020 tokens`

#### Scenario: Поле 17 отклоняется на exact prefix boundary
- **WHEN** source или inline extractor распознает case-sensitive exact field
  prefix и role-local count становится 17
- **THEN** он немедленно возвращает
  `authorization fields exceed 16 values`
- **AND** reject происходит до чтения первого value character, поиска line end,
  trim, enclosing-backtick inspection или сохранения span поля 17
- **AND** extractor не использует `splitlines()` и хранит не более 16 bounded
  admitted offsets/spans
- **AND** instrumented connected oracle падает при любом line-end/content read
  после prefix поля 17, даже если terminal detail совпал

#### Scenario: RFC 8259 number сканируется incremental FSM
- **WHEN** universal scanner встречает number sign, integer, fraction или
  exponent form
- **THEN** он переходит по finite states one character at a time без whole-tail
  regex, fallback parser или rollback
- **AND** на каждом character применяет aggregate/per-value character gates,
  затем syntax transition, затем numeric-length gate для valid continuation
- **AND** valid 64-character numeric lexeme проходит lexical length stage, а
  valid continuation character 65 немедленно получает
  `authorization JSON number exceeds 64 characters`
- **AND** invalid continuation, leading zero, missing fraction/exponent digits,
  bare sign, `+1` или trailing value получают generic syntax detail

#### Scenario: 4301-digit originating regression завершается на character 65
- **WHEN** source или inline connected row содержит valid JSON integer из 4301
  digits и запускает production `run_preflight`
- **THEN** scanner возвращает numeric-length detail exact на numeric character
  65, раньше per-value character limit
- **AND** он не читает и не сканирует character 4097 либо remainder lexeme
- **AND** rows при `PYTHONINTMAXSTRDIGITS=640` и `0` имеют identical exact
  exit/outcome/status/detail/counters, no exception и zero semantic/review/model
  dispatch

#### Scenario: Authorization numeric values не конвертируются
- **WHEN** decoder или source/inline role validator обрабатывает numeric token
- **THEN** token остается immutable parser-owned lexeme и code не вызывает
  `int()`, `float()`, `Decimal()` или user-extensible numeric protocol
- **AND** source ceiling принимает только RFC 8259 integer-form
  integer-not-boolean посредством exact sign/digit/length/lexicographic string
  comparison с bounded decimal range
- **AND** fraction/exponent, boolean, negative, out-of-range или numeric identity
  values получают published role-specific type/range/identity detail до
  mapping, hashing, path или relation semantics

#### Scenario: Prohibited constants требуют exact nested delimiter
- **WHEN** `NaN`, `Infinity` или `-Infinity` появляется на root либо любой
  nesting depth и следующий event есть end, RFC 8259 whitespace, comma, `]` или
  `}`
- **THEN** scanner возвращает
  `authorization JSON must not contain NaN or Infinity`
- **AND** delimiter проходит character gates, но не поглощается и не считается
  token до constant reject
- **AND** `NaNx`, `Infinityx`, `-Infinityx`, lowercase и malformed variants
  получают `authorization JSON must contain exactly one value`
- **AND** только exact lowercase inline literal `none` остается `not-declared`,
  тогда как `NONE` и `None` входят в strict syntax decode

#### Scenario: Pair-preserving roles остаются universal-first
- **WHEN** universal decoder успешно возвращает ordered values
- **THEN** objects остаются immutable ordered pairs, numbers остаются lexemes и
  unvalidated values не используются в hashing, mapping, path construction или
  relation lookup
- **AND** source role сохраняет published typed-hint, one-target, duplicate,
  exact six-field shape, type/range/identity и target-order checks
- **AND** inline role сохраняет exactly-one-value, duplicate decoded key, exact
  two-field shape и non-empty string identity checks до semantics
- **AND** inline role сохраняет details
  `published authorization reference must contain exactly one value`,
  `published authorization reference contains duplicate decoded key: <key>`,
  `authorization reference must contain exactly authorization_card and authorization_id`
  и `authorization reference values must be non-empty strings`

#### Scenario: Structural rejects остаются total и zero-dispatch
- **WHEN** field/resource/syntax/constant/numeric/depth/token/cardinality/
  duplicate/shape/identity gate отклоняет authorization
- **THEN** preflight возвращает exit 1, outcome `investigation-required`,
  authorization `invalid`, exact detail, `llm_review.required: false` и reason
  `complexity guard requires investigation/simplification`
- **AND** semantic, review и model dispatch deltas равны zero и
  `uncaught_exception` равен false
- **AND** semantic relation reject начинается только после validated mapping,
  может иметь один semantic check и сохраняет zero review/model dispatch

#### Scenario: Connected future matrix доказывает новые read gates
- **WHEN** clean incremental implementation готовится к review
- **THEN** production `run_preflight` matrix запускает source и inline rows в
  отдельных processes при `PYTHONINTMAXSTRDIGITS=640` и `0`
- **AND** каждая negative row начинается с fresh passing canonical base и одной
  mutation
- **AND** matrix сохраняет все published constants, number grammar 64/65,
  chars 4096/4097, tokens 255/257, depth 16/17, fields 16/17, aggregate exact/
  over, same-event collision, role structure и phase-routed rows
- **AND** matrix добавляет both-role 4301-digit event-65/no-read-4097 rows,
  field-17 no-line-end/content-read rows, exact nested delimiter/suffix rows и
  no-conversion instrumentation
- **AND** four-run observations имеют identical exact exit/outcome/status/
  detail/reason/counters/exception/dispatch results

#### Scenario: Exhausted identity superseded без history rewrite
- **WHEN** эта investigation опубликована
- **THEN** unpublished
  `authorize-total-bounded-phase-routed-resume-integrity-payload` считается
  `SUPERSEDED`, non-repairable и non-publishable
- **AND** published `6e1cbfa`, failed worktree, tracked artifacts и ignored
  cycle-1/cycle-2 verdict history остаются неизменными
- **AND** superseded id/path никогда не используется как `4.done` source или
  `Published investigation authorization` в новой lineage

#### Scenario: B связывает A только с C
- **WHEN** published A разрешает создать
  `authorize-bounded-incremental-authorization-gate-payload`
- **THEN** B зависит от A и блокирует
  `implement-incremental-authorization-gate-boundary`
- **AND** B содержит ровно один exact six-field object
  `{"investigation_card":"openspec/board/4.done/investigate-incremental-authorization-gate-boundary.md","investigation_id":"investigate-incremental-authorization-gate-boundary","successor_card":"openspec/board/3.inprogress/implement-incremental-authorization-gate-boundary.md","successor_id":"implement-incremental-authorization-gate-boundary","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`
- **AND** B не authorizes existing phase-routed successor и C ссылается только
  на published B exact reference
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-incremental-authorization-gate-payload.md","authorization_id":"authorize-bounded-incremental-authorization-gate-payload"}`

#### Scenario: D связывает A только с existing successor
- **WHEN** C опубликована и разрешено создать
  `authorize-incremental-bounded-phase-routed-resume-integrity-payload`
- **THEN** D зависит от C и блокирует
  `replace-phase-routed-resume-integrity-boundary`
- **AND** D содержит ровно один exact six-field object
  `{"investigation_card":"openspec/board/4.done/investigate-incremental-authorization-gate-boundary.md","investigation_id":"investigate-incremental-authorization-gate-boundary","successor_card":"openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md","successor_id":"replace-phase-routed-resume-integrity-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** D не authorizes C и existing successor ссылается только на published
  D exact reference
  `{"authorization_card":"openspec/board/4.done/authorize-incremental-bounded-phase-routed-resume-integrity-payload.md","authorization_id":"authorize-incremental-bounded-phase-routed-resume-integrity-payload"}`

#### Scenario: Exact clean lineage не содержит shortcut authority
- **WHEN** maintainer планирует downstream work после A
- **THEN** order является exact A -> B -> C -> D ->
  `replace-phase-routed-resume-integrity-boundary`
- **AND** dependency/block relations существуют только между соседними items,
  кроме investigation identity внутри exact source objects B и D
- **AND** отсутствие published предыдущего item fail-closed блокирует создание,
  review и publication следующего

#### Scenario: Investigation verification отделена от implementation evidence
- **WHEN** этот decision-only change доставляется
- **THEN** evidence ограничено card/OpenSpec strict validation, public scan,
  JSON/TOML parse, whitespace и scoped absence runtime/downstream edits
- **AND** RED/GREEN runtime evidence отмечается `not applicable`
- **AND** dual-environment production matrix и полный implementation floor
  остаются future mandatory evidence и не выдаются за planning proof

#### Scenario: Fast-forward остается planning-only
- **WHEN** `$changerail-ff` завершает investigation
- **THEN** создаются только todo card
  `investigate-incremental-authorization-gate-boundary` и active change
  `decide-incremental-authorization-gate-boundary`
- **AND** code, tests, main spec, archive, runtime evidence/history, verdict,
  commit, publish, B, C, D и existing successor не изменяются и не создаются
