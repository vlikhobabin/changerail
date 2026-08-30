# Исследовать admission, hosted-origin и activation closure affected profile v20

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 52

## Source
- Последняя safe published authorization boundary:
  `authorize-bounded-affected-release-profile-v19`, exact commit
  `e3dbdd494f7a8d3dbd10e3b70b9b034d3079b416`.
- Terminal unpublished implementation v19 завершила initial fresh review
  `NO-GO` с acceptance `6/10`, четырьмя blockers, затем единственный
  same-card repair и terminal fresh review `NO-GO` с acceptance `7/10`,
  тремя blockers и exhausted repair budget `1/1/0`.
- Только validated counters и три finding-class summary переходят в эту
  investigation. V19 implementation card/OpenSpec/source/tests/CI/main-spec
  mutation, manifest, verdicts, logs и raw evidence являются forensic-only и
  не читаются, не копируются, не cherry-pick-ятся и не используются как proof.

## Summary
Опубликовать clean docs-only decision для v20, который закрывает порядок
aggregate admission до первого process/Git event, component-safe hosted
toolcache с независимо выведенными из CI targets и единую context-sensitive
activation worklist, из которой непосредственно получаются row reachability и
static/dynamic projections.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: terminal v19 исчерпал единственный repair; admission,
  hosted ancestor containment и activation connectivity требуют нового
  design budget до executable successor.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `authorize-bounded-affected-release-profile-v19`
- `investigate-affected-release-profile-hosted-origin-activation-closure-v19`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v20`
- `implement-bounded-affected-release-profile-v20`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v20 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-admission-hosted-activation-closure-v20.md","investigation_id":"investigate-affected-release-profile-admission-hosted-activation-closure-v20","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v20.md","successor_id":"implement-bounded-affected-release-profile-v20","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision создаётся docs-only из exact published authorization v19 SHA;
  local/upstream/remote investigation branch и remote authorization branch до
  mutation указывают на этот SHA, terminal v19 payload/evidence не
  импортируется, а chronology сохраняет reviews `6/10` и `7/10`, repair
  `1/1/0` и три finding classes.
- Future admission является явной двухфазной state machine: сначала без
  subprocess/Git/scheduler/write/mutation событий валидируются repository,
  immutable registry/operands/origins/packages, runtime root и все selected
  task roots; только после одного aggregate admission barrier разрешаются
  bounded version/usability probes. Independent pre-import observer и
  occupied/dangling/symlinked root neighbors доказывают zero process events до
  barrier и zero later events при любом отказе.
- Hosted oracle независимо парсит exact pinned four-step CI, извлекает
  setup-node action и major `20`, перечисляет ровно один matching `20.x.y` и
  architecture под externally constructed absolute `RUNNER_TOOL_CACHE`, а
  затем строит expected `node`, `npm`, `npx` target/argv только из CI row и
  observed filesystem. Каждый directory component проверяется через `lstat`
  без symlink traversal; bounded npm/npx launcher chain допускается только
  внутри canonical version subtree и сравнивается с independently derived
  target.
- Hosted matrix отвергает missing/relative/outside root, symlink в любом
  directory ancestor, wrong/duplicate version, architecture или token,
  broken/absolute/traversing/escaping/cyclic launcher, zero/multiple targets,
  fake-first selection и hosted-to-system fallback до semantic launch. Для
  `node`, `npm`, `npx` отдельные clean children наблюдают actual target/argv и
  доказывают, что usable fake-first PATH не вызван.
- Activation observer строит один полный source-derived row multiset и одну
  finite context-sensitive worklist от exact public affected entrypoint,
  production arguments и `supervisor=None`. Та же worklist присваивает каждой
  строке reachability/reason, predecessor и transfer rule; static reachable
  call/sink projection вычисляется только фильтрацией этих exact rows, без
  отдельного edge catalog или hardcoded owner exclusions.
- Independently authored immutable `ACTIVATION_CATALOG` сравнивается
  bidirectionally с полным observed multiset по source/digest, item/owner/AST
  path, normalized context/predicates, callee/receiver set, predecessor/
  transfer, reachability/reason и sink class. Owner closure требует, чтобы
  каждый reachable function owner имел reachable entry row и присутствовал в
  projection; extra/missing owner, disconnected row, unknown binding или
  alternate wrapper/sink fail closed.
- Separate pre-import clean child вызывает exact public affected activation и
  отображает externally observed qualified calls/sinks на те же canonical row
  IDs. Dynamic projection сравнивается с projection exact rows той же
  worklist; путь affected→scheduler default→broker sinks наблюдается, а
  non-None supervisor path остаётся cataloged, predicate-backed unreachable.
  Counts-only, self-derived rows, отдельная literal edge list и отсутствие
  trace не принимаются.
- Future authorization зависит ровно от этой investigation, integration
  decision, scheduler v1 и authorization v19 и блокирует только implementation
  v20. Future implementation зависит ровно от тех же predecessors плюс
  authorization v20, блокирует только certification, начинается от
  authorization-publishing HEAD, создаёт новый genuine original RED и
  добавляет максимум `499` production LOC.
- Investigation сохраняет published v18 proof inventory как единственный
  immutable anchor, exact `35/30/48`, semantic digest
  `7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
  full digest
  `6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
  total 35→30 ownership, `36 - 4 - (3 - 1) = 30`, Unicode `23/235`, strict
  four-stream selection, typed scheduler, connected guard mutants, full-only
  authority, protocol-artifact non-authority и exact source-safe four-step CI.
- Investigation меняет только эту card, same-slug OpenSpec, synchronized main
  release-CI spec и archive metadata; production/test/runtime LOC `0`, future
  authorization/implementation/certification отсутствуют, а reachable history,
  real full/affected execution or benchmark, live matrix и certification
  checks не запускаются.

## Change Set
- `investigate-affected-release-profile-admission-hosted-activation-closure-v20`

## Verify
- Required: exact safe base/remotes and forensic boundary; two-phase admission
  barrier and zero-event neighbors; component-safe CI-derived hosted oracle;
  single-worklist row/projection/owner equality; exact future lineage/ceiling;
  successor absence; strict OpenSpec; JSON/TOML; source classification;
  current-only public scan; exact sync; whitespace and manifest scope.
- RED: not applicable; docs-only investigation.
- Prohibited: terminal v19 payload/evidence access, history, real full/affected
  execution or benchmark, live matrix and certification checks.
- Observed: exact local/upstream/remote base and authorization branch passed;
  byte-exact main-spec sync passed; strict OpenSpec after archive `23/23`,
  JSON/TOML, source classification, zero executable LOC, exact relations and
  successor absence, whitespace and manifest scope passed; current-only public
  scan passed `1692/0`. Prohibited checks were not run.

## Archive
- `openspec/changes/archive/2026-08-30-investigate-affected-release-profile-admission-hosted-activation-closure-v20/`

## Related
- `openspec/changes/investigate-affected-release-profile-admission-hosted-activation-closure-v20/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v19.md`
- `openspec/board/4.done/investigate-affected-release-profile-hosted-origin-activation-closure-v19.md`
- `openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: docs-only v20 admission/hosted/activation closure decision
synchronized byte-exactly and archived with zero production/test/runtime LOC;
ready for fresh ordinary/high review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-affected-release-profile-admission-hosted-activation-closure-v20`

### Why
Terminal v19 оставил три blockers после exhausted same-card repair: process
probes до root admission, symlinked hosted ancestor/невыведенный CI oracle и
disconnected activation rows/worklist.

### Goal
Опубликовать feasible independent proof architecture для всех трёх blockers до
любой v20 authorization или executable implementation.

### Scope
- this card;
- same-slug docs-only OpenSpec artifacts;
- synchronized release-CI decision contract and archive metadata.

### Acceptance
- Каждый acceptance criterion карточки проверяем из published source и
  independently authored future proof contracts без terminal payload или
  prohibited execution.

### Depends On
- `authorize-bounded-affected-release-profile-v19`
- `investigate-affected-release-profile-hosted-origin-activation-closure-v19`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/investigate-affected-release-profile-admission-hosted-activation-closure-v20/`

## Log
- 2026-08-30 card created in a clean worktree and remote branch from exact
  published authorization v19 SHA; only validated terminal counters and three
  finding-class summaries crossed the forensic boundary.
- 2026-08-30 FF prepared one docs-only change with a pre-process aggregate
  barrier, component-safe CI-derived hosted oracle, unified activation
  worklist/projection and exact v20 lineage.
- 2026-08-30 DO synchronized six v20 requirements byte-exactly, archived the
  change and passed strict OpenSpec `23/23`, JSON/TOML, source classification,
  zero executable LOC, exact relations/successor absence, current-only public
  scan `1692/0`, whitespace and manifest-scope gates; prohibited checks were
  not run.
- 2026-08-30T08:26:27Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
