# Исследовать hosted-origin и activation closure affected profile v19

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 50

## Source
- Последняя safe published authorization boundary:
  `authorize-bounded-affected-release-profile-v18`, exact commit
  `ea85f2691be7e3a7d61d0ada89fef785233da40e`.
- Terminal unpublished implementation v18 завершил fresh cycle 2 `NO-GO` с
  acceptance `9/11`, двумя blockers и exhausted repair budget `1/1/0`.
- Только validated counters и два finding-class summary переходят в эту
  decision. V18 implementation card/OpenSpec/code/tests/CI/main-spec mutation,
  manifest, verdicts, logs и raw evidence являются forensic-only и не
  читаются, не копируются, не cherry-pick-ятся и не используются как proof.

## Summary
Опубликовать clean docs-only design decision для v19, который требует реально
наблюдать canonical hosted setup-node/`RUNNER_TOOL_CACHE` origin admission и
строить observed context-sensitive activation graph с bidirectional catalog
equality вместо проверки только длины и уникальности каталога.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: terminal v18 исчерпал единственный repair, а activation
  proof остался disconnected после published v18 investigation; до нового
  executable successor обязателен этот design budget.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `authorize-bounded-affected-release-profile-v18`
- `investigate-affected-release-profile-proof-oracle-closure-v18`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v19`
- `implement-bounded-affected-release-profile-v19`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v19 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-hosted-origin-activation-closure-v19.md","investigation_id":"investigate-affected-release-profile-hosted-origin-activation-closure-v19","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v19.md","successor_id":"implement-bounded-affected-release-profile-v19","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision создаётся docs-only из exact published authorization v18 SHA;
  local/upstream/remote investigation branch и remote authorization branch до
  mutation указывают на этот SHA, terminal v18 payload/evidence не импортируется,
  а chronology сохраняет cycle-2 `9/11`, два blockers и repair `1/1/0`.
- Hosted origin proof имеет отдельные clean-child cases для `node`, `npm` и
  `npx`, которые до production import задают externally constructed disposable
  `RUNNER_TOOL_CACHE`, exact setup-node `20` layout и fake-first `PATH`.
  Независимый oracle парсит pinned four-step CI, вычисляет expected canonical
  toolcache targets без production descriptors и наблюдает actual executable
  targets/process argv; каждый case обязан пройти hosted branch, а local
  `_SYSTEM_ORIGINS`, live-PATH или production-declared branch marker не
  считается доказательством.
- Hosted matrix отдельно отвергает absent/relative/symlinked/outside-root
  toolcache, wrong version/architecture/token, zero/multiple targets,
  fake-first usable executable и hosted-to-system fallback. Любая uncertainty
  даёт bounded non-authoritative aggregate failure с `semantic_started:0` и
  externally observed zero Git/scheduler/write/snapshot-delta events.
- Activation proof независимо парсит exact runner/profile и immutable
  scheduler/broker sources, запускает deterministic context-sensitive worklist
  от exact public affected entrypoint и production argument row с
  `supervisor=None`, и материализует observed rows для every import/binding/
  call/predicate/raw sink с canonical source identity, callsite, context,
  finite callee/receiver set, reachability и reason.
- Independently authored `ACTIVATION_CATALOG` сравнивается bidirectionally с
  реально materialized observed row set по exact identities and fields.
  Length/uniqueness, self-derived rows, missing observed rows, unused catalog
  rows, unknown/empty/ambiguous bindings, runtime rebind и latent-to-reachable
  transition fail closed.
- Clean-child public activation witness с pre-import profile/audit hooks
  наблюдает exact reachable affected→scheduler-default→broker call/sink edges
  и exact production arguments. Static observed graph и dynamic trace обязаны
  совпасть на reachable projection; injected non-None supervisor path остаётся
  cataloged и predicate-backed unreachable, а alternate wrapper/raw sink не
  принимается.
- Future authorization зависит ровно от этой investigation, integration
  decision, scheduler v1 и authorization v18 и блокирует только implementation
  v19. Future implementation зависит ровно от тех же predecessors плюс
  authorization v19, блокирует только certification, начинается от
  authorization-publishing HEAD, создаёт новый genuine original RED и
  добавляет максимум `499` production LOC.
- Investigation сохраняет published v18 proof inventory/digests, exact 35→30,
  Unicode `23/235`, aggregate admission, strict four-stream selector, typed
  scheduler, connected guard mutants, full-only authority, protocol-artifact
  non-authority, source-safe four-step CI и весь accumulated floor.
- Investigation меняет только эту card, same-slug OpenSpec, synchronized main
  spec и archive metadata; production/test/runtime LOC `0`, successors
  отсутствуют, а reachable history, real full/affected execution or benchmark,
  live matrix и certification checks не запускаются.

## Change Set
- `investigate-affected-release-profile-hosted-origin-activation-closure-v19`

## Verify
- Required: exact safe base/remotes, terminal chronology/forensic boundary,
  hosted origin case/token coverage, independently derived toolcache targets,
  observed activation rows and bidirectional equality, dynamic reachable
  witness, exact future lineage/ceiling, successor absence, strict OpenSpec,
  JSON/TOML, source classification, current-only public scan, exact sync,
  whitespace and manifest scope.
- RED: not applicable; docs-only investigation.
- Prohibited: terminal v18 payload/evidence access, history, real full/affected
  execution or benchmark, live matrix and certification checks.
- Observed: exact local/upstream/remote base and authorization branch passed;
  hosted token/negative-neighbor and observed-graph/dynamic-witness contracts
  are present; byte-exact main-spec sync passed; strict OpenSpec after archive
  `23/23`, JSON/TOML, source classification, zero executable LOC, exact
  relations/successor absence and whitespace passed; current-only public scan
  passed `1680/0`.

## Archive
- `openspec/changes/archive/2026-08-29-investigate-affected-release-profile-hosted-origin-activation-closure-v19/`

## Related
- `openspec/changes/investigate-affected-release-profile-hosted-origin-activation-closure-v19/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v18.md`
- `openspec/board/4.done/investigate-affected-release-profile-proof-oracle-closure-v18.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: docs-only hosted-origin and observed-activation closure decision
synchronized and archived with zero production/test/runtime LOC; ready for
fresh ordinary/high review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-affected-release-profile-hosted-origin-activation-closure-v19`

### Why
Terminal v18 оставил непройденными canonical hosted-origin branch и реальное
построение activation graph; exhausted repair запрещает ещё один same-card fix.

### Goal
Опубликовать feasible independent proof architecture для обоих blockers до
любой v19 authorization или executable implementation.

### Scope
- this card;
- same-slug docs-only OpenSpec artifacts;
- synchronized release-CI decision contract and archive metadata.

### Acceptance
- Каждый acceptance criterion карточки проверяем из published source и
  independently authored proof contracts без terminal payload или prohibited
  execution.

### Depends On
- `authorize-bounded-affected-release-profile-v18`
- `investigate-affected-release-profile-proof-oracle-closure-v18`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/investigate-affected-release-profile-hosted-origin-activation-closure-v19/`

## Log
- 2026-08-29 card created in a clean worktree and remote branch from exact
  published authorization v18 SHA; only validated terminal counters and two
  finding-class summaries crossed the forensic boundary.
- 2026-08-29 FF prepared one docs-only change with token-specific hosted
  setup-node/toolcache observation, a source-derived activation worklist,
  bidirectional catalog equality, dynamic reachable witnesses and exact v19
  lineage.
- 2026-08-29 DO synchronized the release-CI delta byte-exactly, archived the
  change and passed exact-base, strict OpenSpec, JSON/TOML, source
  classification, current-only public scan `1680/0`, successor absence and
  whitespace gates with zero executable LOC; prohibited checks were not run.
- 2026-08-29 deterministic preflight process correction marked this docs-only
  investigation payload itself as not introducing a repeated defect class;
  lineage escalation remains explicit and no semantic review cycle was used.
- 2026-08-29T20:38:29Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
