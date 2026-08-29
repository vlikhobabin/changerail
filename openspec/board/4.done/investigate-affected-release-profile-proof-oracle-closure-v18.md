# Исследовать замыкание proof oracle affected profile v18

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 47

## Source
- Последняя safe published authorization boundary:
  `authorize-bounded-affected-release-profile-v17`, exact commit
  `fdff98a2fbf962182b2d5777f9c5cc6e33e6cf17`.
- Terminal unpublished implementation v17 завершил fresh cycle 1 `NO-GO`
  с `4/10` и пятью blockers, использовал единственный same-card repair и
  завершил cycle 2 `NO-GO` с `5/10`, тремя blockers и budget `1/1/0`
  exhausted.
- Только validated counters и три finding-class summary переходят в эту
  decision. V17 card/OpenSpec/code/tests/CI/spec mutation/manifest/verdicts,
  logs и raw evidence являются forensic-only и не читаются, не копируются и
  не cherry-pick-ятся.

## Summary
Опубликовать clean docs-only design decision для v18, который устраняет три
повторившихся класса self-derived proof: scheduler catalogs/mutants,
closed-graph/resolved-base connectivity и tautological registry/ledger
наблюдения.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: terminal v17 исчерпал единственный repair, а три
  proof-oracle класса повторили unresolved invariants после clean
  investigations v16/v17; до нового executable successor обязателен этот
  design budget.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `authorize-bounded-affected-release-profile-v17`
- `investigate-affected-release-profile-semantic-proof-closure-v17`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v18`
- `implement-bounded-affected-release-profile-v18`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v18 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-proof-oracle-closure-v18.md","investigation_id":"investigate-affected-release-profile-proof-oracle-closure-v18","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v18.md","successor_id":"implement-bounded-affected-release-profile-v18","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision создаётся docs-only из exact published authorization v17 SHA;
  local/upstream/remote investigation branch и remote authorization branch до
  mutation указывают на этот SHA, terminal v17 executable payload/evidence не
  импортируются, а chronology сохраняет `4/10 → 5/10`, пять → три blockers и
  repair `1/1/0`.
- Scheduler proof использует четыре независимо authored immutable catalog:
  normative cases, executable cases, requirement guards и mutants. Ни один
  catalog не выводится из другого или production registry; bidirectional
  equality, pinned repository path/qualified function/canonical AST node path,
  source digest и canonical before/after digests проверяются отдельно.
- Closed mutation language допускает только замену одного существующего AST
  operator/operand в pinned node. Whole-tree comparison отвергает добавленный
  control flow, generated code, payload predicate, wrapper, early
  return/raise, marker/no-op/reused edit; mapped public neighbor достигает
  target в original и mutant trace и расходится только после target, поэтому
  earlier-fault masking не считается kill.
- Closed execution-graph oracle строит полный import/binding/call graph из
  canonical runner/profile/scheduler/broker sources и сравнивает его с
  independently authored edge/sink catalog. Affected-owned runner/profile
  ограничены direct statically bound calls и вызывают scheduler только с exact
  production arguments, включая `supervisor=None`. Exact immutable published
  scheduler/broker digests используют отдельный legacy-edge catalog и полный
  syntactic inventory. Context-sensitive reachability разрешает finite unique
  bindings только на достижимой default path; published injection callback и
  другие higher-order nodes остаются cataloged, но доказанно unreachable из
  affected activation. Non-None supervisor, новый/unknown/rebound/dynamic edge
  или raw sink fail closed без изменения predecessor modules.
- Каждый resolved-base, four-stream collector и bounded-fallback guard имеет
  отдельный connected mutant ровно в canonical production node и public case,
  который проходит через explicit admitted root и honest disposable Git.
  Guard IDs, connected case refs и mutant IDs равны bidirectionally; ни один
  private/disconnected helper не принимается.
- Future authorization независимо публикует immutable normative inventory и
  SHA-256: exact 35 semantic ID/owner rows, exact 30 physical task command rows
  с typed operand kind/value/location/grammar и origin, total 35→30 ownership
  map и все non-task targets. Legacy 36-Step baseline не считается этим
  inventory; static migration oracle отдельно доказывает сохранение semantics
  и approved grouping. Production registry, extraction и independent proof
  parser каждый сравниваются с уже опубликованным anchor, поэтому coordinated
  command/descriptor drift fail closed.
- Admission side effects доказываются только externally observed clean-child
  events: pre-import audit/profile hooks фиксируют process/Git/scheduler и
  write-intent calls, а before/after filesystem snapshots фиксируют mutation.
  Production-declared empty ledgers, monkeypatches и заменённые results не
  принимаются; каждый fake-first admission case доказывает zero later events.
- Future authorization зависит ровно от этой investigation, integration
  decision, scheduler v1 и authorization v17 и блокирует только implementation
  v18. Future implementation зависит ровно от тех же predecessors плюс
  authorization v18, блокирует только certification, начинается от
  authorization-publishing HEAD, создаёт новый genuine original RED и
  добавляет максимум `499` production LOC.
- Investigation сохраняет exact 35→30/Unicode `23/235`, aggregate admission,
  strict four-stream selector, typed scheduler, full-only authority,
  protocol-artifact non-authority, source-safe four-step CI и весь accumulated
  published floor. Она меняет только card, same-slug OpenSpec, synchronized
  main spec и archive metadata; executable LOC `0`, successors отсутствуют,
  prohibited release/certification checks не запускаются.

## Change Set
- `investigate-affected-release-profile-proof-oracle-closure-v18`

## Verify
- Required: exact safe base/remote, terminal chronology/forensic boundary,
  independent catalogs and mutation language, closed structural call graph,
  connected guard mutants, independent operand parsing, external event
  observation, exact future lineage/ceiling, successor absence, strict
  OpenSpec, JSON/TOML, source classification, current-only public scan, sync,
  whitespace and manifest scope.
- RED: not applicable; docs-only investigation.
- Prohibited: terminal v17 payload/evidence access, history, real full/affected
  execution or benchmark, live matrix and certification checks.
- Observed: exact base/remote passed; strict target/capability/all OpenSpec
  passed before archive `24/24`; JSON/TOML parsing, exact main-spec sync,
  source classification, zero executable LOC, successor absence and whitespace
  passed; current-only public scan passed `1667/0`.

## Archive
- `openspec/changes/archive/2026-08-29-investigate-affected-release-profile-proof-oracle-closure-v18/`

## Related
- `openspec/changes/investigate-affected-release-profile-proof-oracle-closure-v18/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v17.md`
- `openspec/board/4.done/investigate-affected-release-profile-semantic-proof-closure-v17.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: docs-only proof-oracle closure decision synchronized and archived
with zero production/test/runtime LOC; ready for fresh ordinary/high review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-affected-release-profile-proof-oracle-closure-v18`

### Why
Terminal v17 закрыл два прежних blocker, но три оставшихся proof classes всё
ещё позволяли self-derived catalogs, dynamic execution bypasses, disconnected
mutants и production-declared observations.

### Goal
Опубликовать feasible independent proof architecture до любой новой
authorization или executable implementation.

### Scope
- this card;
- same-slug docs-only OpenSpec artifacts;
- synchronized release-CI decision contract and archive metadata.

### Acceptance
- Каждый acceptance criterion карточки проверяем из published source и
  independently authored proof contracts без terminal payload или prohibited
  execution.

### Depends On
- `authorize-bounded-affected-release-profile-v17`
- `investigate-affected-release-profile-semantic-proof-closure-v17`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/investigate-affected-release-profile-proof-oracle-closure-v18/`

## Log
- 2026-08-29 card created in a clean worktree and remote branch from exact
  published authorization v17 SHA; only validated terminal counters and three
  finding-class summaries crossed the forensic boundary.
- 2026-08-29 FF prepared one docs-only change with sealed independent catalogs,
  closed mutation/call-graph languages, connected guard mutants, independent
  operand parsing, external event observation and exact v18 lineage; strict
  OpenSpec passed `24/24`.
- 2026-08-29 DO synchronized the release-CI delta byte-exactly, archived the
  change and passed exact-base, strict OpenSpec, JSON/TOML, source
  classification, current-only public scan `1667/0`, successor absence and
  whitespace gates with zero executable LOC; prohibited checks were not run.
- 2026-08-29 fresh ordinary/high review cycle 1 returned `NO-GO` with `7/9`
  acceptance and two docs blockers: the graph language rejected immutable
  published scheduler/broker shapes, and the ID-only digest did not anchor
  command/operand bytes. One bounded same-card repair was consumed.
- 2026-08-29 repair partitioned strict affected-owned calls from exact-digest
  legacy scheduler/broker dataflow and required authorization v18 to publish an
  independently reviewed canonical command/typed-operand inventory digest
  before implementation; no executable scope or predecessor mutation was
  added. Fresh cycle-2 review required.
- 2026-08-29 pre-verdict feasibility audit уточнил graph contract: complete
  syntax inventory отделён от context-sensitive activation reachability;
  affected caller обязан передавать published scheduler `supervisor=None`, а
  immutable injection callback остаётся cataloged but unreachable. Review был
  остановлен до verdict, payload обновлён и требует нового exact preflight.
- 2026-08-29 второй pre-verdict audit выявил cardinality ambiguity: текущие 36
  legacy baseline steps не равны ни 35 semantic IDs, ни будущим 30 physical
  tasks. Review остановлен до verdict; inventory разделён на exact 35 semantic,
  30 physical и non-task sections с total mapping и static migration oracle.
- 2026-08-29T16:49:56Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
