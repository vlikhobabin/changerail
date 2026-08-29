## Context

Published v17 разделил pure `R/C 000..100` grammar и honest real-Git emission,
а scheduler cases привязал к semantic guards вместо ложного равенства
case/mutant cardinality. Clean implementation v17 после одного repair закрыл
два finding-class, но terminal review всё ещё обнаружил три независимых
проблемы доказательства:

1. catalogs и `guard_id` relations выводились из совместно управляемых данных,
   canonical source anchors не были полностью pinned, а mutation validator не
   исключал другой control flow и earlier-fault kills;
2. closed graph был blacklist-проверкой и пропускал dynamic call expressions,
   wrappers и closure-shaped bypasses; большинство resolved-base/collector
   guards не имели connected mutation в реальном source;
3. command descriptors сравнивались без независимого разбора direct/embedded
   operands, а zero-side-effect proof доверял production-owned empty arrays и
   наблюдал не все Git/scheduler/mutation boundaries.

Terminal v17 tree, card, OpenSpec, tests, CI, spec mutation, runtime evidence и
verdict files остаются forensic-only. Этот change использует только published
v17 authorization HEAD и validated summary `4/10 → 5/10`, `5 → 3 blockers`,
repair `1/1/0`.

## Goals / Non-Goals

**Goals:**

- сделать completeness relations cross-authored и проверяемыми без общего
  generator/source of expected truth;
- разрешить только closed single-node mutation language и доказать, что kill
  происходит после достижения target guard;
- заменить blacklist execution scan на полный whitelist call graph;
- связать каждый base/collector/fallback guard с actual-source mutation и
  public explicit-root case;
- разделить declared targets, production extraction, proof parsing и external
  side-effect observation;
- оставить v18 executable scope bounded до `499` added production LOC и
  сохранить весь accumulated full-only-authority floor.

**Non-Goals:**

- не реализовывать или авторизовывать v18 в этой карточке;
- не читать и не воспроизводить terminal v17 payload/evidence;
- не запускать reachable-history, real full/affected execution, benchmark,
  live matrix или certification;
- не менять scheduler/broker internals и не давать affected/protocol artifacts
  publication authority.

## Decisions

### 1. Four sealed catalogs, no derivation edges

Future v18 хранит normative cases, executable cases, requirement guards и
semantic mutants как четыре literal immutable inventories. Test loader может
читать их для сравнения, но ни один catalog не импортирует, не генерирует и не
дополняет другой; production не экспортирует expected catalog. Static oracle
проверяет отсутствие derivation/import edges и отдельно сравнивает:

- normative case IDs ↔ executable case IDs;
- requirement guard IDs ↔ case-referenced guard IDs ↔ mutant guard IDs;
- один guard → один mutant и не менее одного passing/invalid neighbor;
- каждый executable case → ровно один guard и exact public expected outcome.

Каждый guard/mutant pin содержит repository-relative module path, qualified
function, canonical AST field/index path, source digest, node kind и canonical
before/after AST digests. Source digest и node paths вычисляются из reviewed
tree, а catalog содержит literal expected values; вычисленный результат
сравнивается с ним, но не записывает или regenerates его.

Альтернатива — один generated catalog — короче, но снова позволяет coordinated
drift и поэтому отклонена.

### 2. Closed single-node mutation language with reachability proof

Mutation descriptor разрешает ровно одну замену существующего operator или
operand в pinned AST path. Validator независимо парсит original source, находит
ровно один node, строит mutant и сравнивает canonical whole-module AST:

- все nodes/fields, кроме declared target value, byte-identical canonically;
- число и расположение statement/control-flow/call nodes не меняются;
- before/after различны, unique среди catalog и совпадают с literal digests;
- target kind и replacement входят в небольшую allowlist;
- compile не использует source strings, `exec` или injected helpers.

Для kill mapped case сначала проходит public boundary на original. Отдельные
trace observations подтверждают достижение exact target source span и original,
и mutant до первого различия. Mutant принимается только если затем меняется
declared public outcome для того же case; exception до target, unexpected
setup failure или divergence в prerequisite trace rejected. Это исключает
early return/raise, payload predicate, wrapper, no-op, reused edit и
earlier-fault masking.

### 3. Partitioned whitelist resolver and exact connected guard inventory

Oracle парсит canonical runner, profile, scheduler и broker modules, строит
полные import/binding/function/call inventories и сравнивает их bidirectionally
с двумя независимо authored partitions одного edge/sink catalog.

Affected-owned runner/profile partition разрешает только direct `Name(...)`
local/pinned builtin calls, exact one-level `module_alias.member(...)` и
перечисленный scheduler entrypoint. Callable parameters/assignments, lambda,
nested function/closure, call/subscript-valued callee, unresolved nested
attribute и raw execution sink в affected-owned source fail closed.

Immutable published scheduler/broker partition pin-ит exact repository path и
whole-source digest predecessor modules. Его independently authored legacy
edge rows явно перечисляют все существующие callable parameters, lambda AST
paths/captures, nested functions, callable assignments and nested attributes,
включая public test-injection `supervisor` path. Это complete syntactic
inventory, а не утверждение, что каждый latent callback активен.

Отдельный context-sensitive activation graph стартует только от exact
affected-owned public entrypoint и exact argument rows. Affected production
MUST invoke scheduler `run_plan` without override, equivalently with
`supervisor=None`. Closed constant/branch/dataflow resolution поэтому достигает
default `_broker_supervise` lambda, finite executor/submit/start callees и exact
broker sinks, но помечает `_injected_call` и arbitrary external supervisor
callback cataloged-but-unreachable. Каждый activation-reachable higher-order
node обязан иметь конечное непустое exact qualified callee/receiver set; каждый
latent node обязан иметь explicit unreachable reason tied to the exact branch
predicate and argument binding. Catalog/observed syntax and reachable/unreachable
classifications сравниваются bidirectionally.

Non-None affected supervisor, изменённый argument row/source digest, новая
higher-order shape, latent-to-reachable transition, unknown/empty/undeclared
ambiguous reachable binding, runtime rebind или edge вне catalog fail closed и
требует отдельного predecessor refactor authorization, а не mutation affected
successor. Так immutable scheduler injection API остаётся доступным его focused
tests, но не становится production escape edge affected profile.

Во всех partitions `__import__`, dynamic `getattr`, importlib, `eval`, `exec`,
`compile`, unbound dynamic dispatch и alternate subprocess/`os.system`/
shell-equivalent sites запрещены. Exact existing broker raw sinks отдельно
pinned; affected-owned graph достигает их только через reachable published
scheduler default and broker entry edges. Wrapper допустим лишь как cataloged
exact-digest edge с полностью разрешёнными reachable incoming/outgoing bindings
или explicit predicate-backed unreachable classification.

Guard catalog перечисляет каждый resolved-base, stream collector и fallback
decision node. Для каждого ID требуется один mutant в canonical production
node и минимум один mapped public case через explicit admitted repository root;
collector cases используют honest disposable Git. Равенство guard IDs,
connected case references и mutant IDs проверяется bidirectionally.

### 4. Three-way operand truth and external-only observation

До implementation future authorization v18 публикует separately authored
immutable normative inventory и lowercase SHA-256. Inventory имеет три exact
sections и не смешивает semantic cardinality с process cardinality:

- 35 ordered semantic rows `logical_id, owner` с published newline digest;
- 30 ordered physical task rows `task_id, command_kind, exact tokens, origin,
  typed operands, owned_logical_ids`;
- все non-task target rows, нужные aggregate admission.

Canonical digest preimage — deterministic length-framed UTF-8 serialization
всех section tags, row counts, fixed keys, exact token bytes и каждого operand
kind/value/token location или embedded grammar location. Ownership map обязан
быть total/bidirectional: каждый из 35 IDs встречается ровно в одном physical
row, каждый из 30 tasks владеет непустым ordered ID set, а Windows matrix row
владеет ровно шестью published leaves без aggregator PASS.

Текущие 36 legacy `Step(...)` calls в `scripts/run-release-baseline.py` не
являются 35 semantic rows или будущими 30 physical rows и не сравниваются по
ложному cardinality equality. Authorization review независимо сверяет semantic
section с published 35-ID list, physical commands/targets с published future
35→30 ownership requirements и authorization-HEAD source, а static migration
oracle доказывает, что каждый legacy mandatory semantic owner сохранён ровно
один раз, включая approved Windows grouping/removals, без запуска baseline.

Single production registry затем хранит literal command representation и typed
target descriptors. Production extractor разбирает registry commands для
admission. Независимый proof parser не импортирует production extractor,
production descriptors или expected multiset и отдельно разбирает direct argv
и embedded shell operands по closed grammar. Production rows, production
extraction и proof-parser rows каждый bidirectionally сравниваются с уже
published authorization physical/non-task sections и recomputed full digest;
exact 30-task cardinality, token bytes, type, decoded value, position, origin,
ID and 35→30 owner map обязательны.
35-ID newline digest остаётся отдельным inventory-order check и не считается
command anchor. Поэтому coordinated command+descriptor drift требует изменить
раньше опубликованный authorization artifact и делает reference/fresh review
невалидными.

Production-owned event arrays не являются evidence. Clean child устанавливает
Python audit/profile hooks до production import. Audit events независимо
классифицируют process and exact Git argv, write-intent filesystem operations;
profile events фиксируют calls в pinned scheduler entrypoint и admitted
mutation functions по code filename/qualname. External before/after snapshots
дополняют mutation ledger. Hooks не заменяют production functions, constants,
return values или calls. Для каждого fake-first admission fault evidence
должно показывать `semantic_started:0` и ноль process/Git/scheduler/write/snapshot
events после fault boundary.

### 5. One bounded successor path

После публикации decision создаётся отдельная docs-only authorization v18 с
exact six-field object:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-proof-oracle-closure-v18.md","investigation_id":"investigate-affected-release-profile-proof-oracle-closure-v18","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v18.md","successor_id":"implement-bounded-affected-release-profile-v18","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization зависит ровно от investigation v18, integration decision,
scheduler v1 и authorization v17 и блокирует только implementation v18.
Вне six-field object authorization публикует proof-only normative semantic/
command/typed-operand/ownership inventory и его canonical digest; это не
production registry, runtime authority или дополнительное поле authorization
object.
Implementation использует только exact two-field authorization v18 reference,
зависит от этих четырёх predecessors плюс authorization v18, блокирует только
certification, стартует от authorization-publishing HEAD, создаёт новый
retained original RED до executable mutation и добавляет максимум `499`
production LOC.

## Risks / Trade-offs

- [Partitioned resolver сложнее простого shape blacklist] → exact predecessor
  source digests, complete syntax inventory, exact activation arguments и
  bidirectional reachable/unreachable bindings закрывают только уже
  опубликованные shapes; новый или latent-to-reachable edge требует отдельного
  authorized predecessor change и fresh review.
- [Trace может зависеть от line/span stability] → canonical AST path и source
  digest являются authority, а trace лишь independently confirms reachability;
  любой mismatch fail closed.
- [Audit/profile hooks не видят произвольную native mutation] → affected
  surface не допускает неперечисленные native/dynamic sinks, structural graph
  закрывает escape path, а filesystem snapshots дают второй внешний канал.
- [Четыре literal catalog увеличивают test payload] → production ceiling не
  расходуется, а независимость и bidirectional completeness важнее duplication.
- [Shell grammar может быть неоднозначной] → неполный или неоднозначный parse
  является admission failure; registry предпочитает argv и допускает только
  bounded declared embedded grammar.

## Migration Plan

1. Опубликовать эту docs-only investigation после fresh ordinary/high review.
2. Отдельно опубликовать exact authorization v18.
3. Создать clean implementation v18 от authorization HEAD и получить genuine
   original RED до production/CI/main-spec mutation.
4. Реализовать только published contracts, пройти focused/static/current gates,
   fresh ordinary/high review и publish.
5. Только затем создать final critical certification card.

Rollback до implementation — не создавать следующий successor. Unpublished
v18 executable failure снова остаётся forensic-only; publication authority
остаётся исключительно у успешного full-release.

## Open Questions

- none; ambiguity в call shape, operand grammar, event mapping или guard
  connectivity должна fail closed, а не решаться runtime inference.
