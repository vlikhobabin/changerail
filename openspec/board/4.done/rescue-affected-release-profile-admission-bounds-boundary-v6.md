# Исследовать и закрыть admission/bounds boundary affected profile v6

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 15S

## Source
- Latest safe published affected v5 authorization, exact tip
  `3588c1d3de0ddc9d8ef50e81992620fc107e4e90`.
- Published RED-evidence rescue, integration decision, semantic scheduler v1
  and affected v5 authorization.
- Unpublished `implement-bounded-affected-release-profile-v5` ended after one
  repair in terminal review-cycle-2 `NO-GO`; its code, card, manifest,
  verdicts, logs and evidence are forensic-only and cannot satisfy future gates.

## Summary
Опубликовать docs-only investigation/design boundary для clean affected v6:
runtime-output admission обязан предшествовать любому filesystem creation и
fail closed на существующем wrong-type/symlink/inaccessible target, а finite
connected mutation matrix обязана отдельно доказать `MAX_PATH`, `MAX_PATHS`,
per-stream и aggregate `MAX_GIT_BYTES` guards.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: this docs-only investigation/design is required because
  multiple affected-profile generations repeated proof-completeness defects.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `rescue-affected-release-profile-red-evidence-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v5`

## Blocks
- `authorize-bounded-affected-release-profile-v6`
- `implement-bounded-affected-release-profile-v6`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v6 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md","investigation_id":"rescue-affected-release-profile-admission-bounds-boundary-v6","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v6.md","successor_id":"implement-bounded-affected-release-profile-v6","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision публикуется docs-only от exact safe v5 authorization tip
  `3588c1d3...`; remote rescue branch начинается ровно от этого SHA, а terminal
  v5 payload не читается, не копируется, не cherry-pick-ится и не принимается.
- Card переносит concise terminal chronology: cycle 1 `NO-GO` имел `10/12` и
  два blocker, единственная repair была израсходована, cycle 2 `NO-GO` имел
  `9/12` и два blocker; current hypothesis ограничена runtime-output admission
  и недостающими selector-bound counterfactuals.
- Единственный future order: эта investigation/design decision, docs-only
  `authorize-bounded-affected-release-profile-v6`, clean
  `implement-bounded-affected-release-profile-v6`, затем certification.
- Future authorization содержит ровно один exact six-field object выше,
  зависит ровно от этой decision, integration decision, scheduler v1 и v5
  authorization и блокирует только v6 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v6.md","authorization_id":"authorize-bounded-affected-release-profile-v6"}`,
  зависит от этих четырёх predecessors плюс authorization v6, блокирует только
  certification, начинается от authorization-publishing HEAD и добавляет не
  более 499 production LOC.
- Aggregate admission до selection, semantics и filesystem mutation проверяет
  runtime-output target: absent path допустим только под real writable/searchable
  repository-local parent; existing path допустим только как real non-symlink
  writable/searchable directory. Existing file, symlink, wrong type, escaping,
  inaccessible или uncertain parent дают bounded report с
  `semantic_started: 0`; `main()` не выбрасывает exception до report.
- Focused proof содержит отдельные connected happy/fault fixtures и non-noop
  production-guard mutants для per-path `MAX_PATH`, aggregate/deduplicated
  `MAX_PATHS`, каждого committed/staged/unstaged/untracked stream
  `MAX_GIT_BYTES` и aggregate four-stream `MAX_GIT_BYTES`; удаление или
  ослабление exact guard делает named fixture красной.
- Target proof отдельно достигает runtime-output existing-file, symlink,
  wrong-type, root-escape и access faults через реальный aggregate admission,
  доказывает `semantic_started: 0` и содержит counterfactual, который меняет
  exact filesystem/admission ordering либо type guard.
- Future v6 сохраняет retained pre-production RED chronology и весь published
  v5 floor: exact 35→30 ownership, strict four-stream grammar, typed scheduler,
  full-only authority, source-safe four-step CI, connected resolved-base guards
  и protocol-artifact non-authority.
- Decision добавляет production/test/runtime LOC 0, не создаёт v6 successors и
  не запускает history, real full/affected execution, benchmark, live matrix
  или certification checks.

## Change Set
- `rescue-affected-release-profile-admission-bounds-boundary-v6`

## Verify
- GREEN retained: `safe-base-remote-binding`, `lineage-successor-absence`,
  `post-archive-contract-scope` and `post-archive-current-public-scan` prove
  exact source SHA/remote branch, lineage/object/reference/
  dependency/order/absence, terminal-attempt summary, runtime-output ordering/
  type boundary, complete selector-bound mutation inventory, preserved v5
  floor, strict OpenSpec, JSON/TOML, current public scan, source classification,
  whitespace, archive/main sync and manifest scope; normalized ordinary/high
  preflight is required before review.
- RED: not applicable; this docs-only investigation/design adds no executable behavior.
- Prohibited: history, real full baseline, affected execution/benchmark, live
  matrix, successor creation/implementation and certification.

## Archive
- `openspec/changes/archive/2026-08-27-rescue-affected-release-profile-admission-bounds-boundary-v6/`

## Related
- `openspec/changes/rescue-affected-release-profile-admission-bounds-boundary-v6/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md`
- `openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: one docs-only investigation/design decision is synchronized and
archived. Exact v6 lineage, runtime-output admission ordering and connected
selector-bound proof are review-ready; successors and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-affected-release-profile-admission-bounds-boundary-v6`

### Why
Affected v5 exhausted its sole repair with an unbounded pre-admission
runtime-output type fault and an incomplete selector-bound mutation proof;
another same-card patch or implementation rescue would violate lifecycle policy.

### Goal
Publish one clean docs-only investigation/design decision that makes the v6
admission ordering, runtime-output types and selector-bound counterfactuals exact.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact lineage, terminal-attempt summary, runtime-output admission ordering,
  selector-bound mutation inventory, preserved v5 floor, LOC, dormancy and
  prohibited-suite boundaries above are synchronized.

### Depends On
- `rescue-affected-release-profile-red-evidence-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v5`

### Related
- `openspec/changes/rescue-affected-release-profile-admission-bounds-boundary-v6/`

## Log
- 2026-08-27 created in a clean worktree and remote branch from exact safe v5
  authorization tip; terminal v5 payload was not imported or executed.
- 2026-08-27 FF produced one apply-ready docs-only investigation/design change;
  v6 successors, executable LOC and prohibited evidence remain absent.
- 2026-08-27 DO retained exact safe-base/remote and lineage/absence evidence,
  synchronized four release-CI requirements, archived the same-slug change and
  passed strict/config/classification/current-public/whitespace checks with
  production/test/runtime LOC `0`; prohibited execution remained absent.
- 2026-08-27T07:42:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
