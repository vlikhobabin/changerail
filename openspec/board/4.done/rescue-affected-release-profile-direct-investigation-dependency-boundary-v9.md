# Спасти direct investigation dependency boundary affected profile v9

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 23S

## Source
- Latest safe published affected v8 authorization, exact tip
  `5b4981f92e55bec4644fef100171bb3e83f00cc1`.
- Published v8 contract-closure investigation, integration decision, semantic
  scheduler v1 and affected v7/v8 authorizations.
- Unpublished `implement-bounded-affected-release-profile-v8` stopped before
  review because deterministic preflight found a contradiction between the
  generic direct-investigation dependency gate and the published exact v8
  dependency set; its entire payload and runtime state are forensic-only.

## Summary
Опубликовать docs-only investigation/design decision, которая закрывает
противоречие direct-investigation dependency gate: terminal v8 не изменяется и
не переиспользуется, а clean v9 lineage получает отдельную authorization и
прямую зависимость implementation от этой rescue decision.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: executable v8 contract оказался внутренне
  неприменимым на deterministic preflight, поэтому дальнейшая implementation
  требует отдельного investigation/design contract, а не обхода gate.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `investigate-affected-release-profile-contract-closure-boundary-v8`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v7`
- `authorize-bounded-affected-release-profile-v8`

## Blocks
- `authorize-bounded-affected-release-profile-v9`
- `implement-bounded-affected-release-profile-v9`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v9 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-direct-investigation-dependency-boundary-v9.md","investigation_id":"rescue-affected-release-profile-direct-investigation-dependency-boundary-v9","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v9.md","successor_id":"implement-bounded-affected-release-profile-v9","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision публикуется docs-only от exact safe v8 authorization tip
  `5b4981f...`; remote authorization и rescue branches до mutation указывают
  ровно на этот SHA, а unpublished v8 payload/evidence не читаются, не
  копируются, не cherry-pick-ятся и не принимаются.
- Card сохраняет только concise v8 chronology: clean implementation началась
  от published authorization, retained pre-production RED была валидной,
  focused/static/current checks прошли, deterministic preflight остановил
  review из-за конфликта direct-investigation dependency validation с
  published exact dependency set; review и publish не запускались.
- Terminal v8 является forensic-only и не исправляется. Ни direct-investigation
  gate, ни published exact v8 contract не ослабляются и не обходятся.
- Единственный future order: эта rescue investigation/design decision,
  docs-only `authorize-bounded-affected-release-profile-v9`, clean
  `implement-bounded-affected-release-profile-v9`, затем certification.
- Future authorization содержит ровно один exact six-field object выше,
  зависит ровно от этой rescue decision, integration decision, scheduler v1 и
  affected v8 authorization и блокирует только implementation v9.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v9.md","authorization_id":"authorize-bounded-affected-release-profile-v9"}`,
  зависит ровно от этой rescue decision, integration decision, scheduler v1,
  affected v8 authorization и authorization v9, блокирует только
  `certify-accelerated-release-loop-v1`, начинается от authorization-publishing
  HEAD и добавляет не более 499 production LOC.
- Future v9 сохраняет retained real pre-production RED с fingerprint перед
  direct non-zero focused test, reachable saved tree и reconstruction против
  authorization HEAD до production, CI или main-spec mutation.
- Future v9 сохраняет exact 35-ID digest и 35→30 ownership, exhaustive frozen
  typed registry и aggregate pre-mutation admission, effective
  `purelib`/`platlib` origins, strict four-stream selector, typed scheduler,
  full-only authority, exact source-safe four-step CI, closed import/call/raw
  execution ownership, source-connected guard mutants и protocol-artifact
  non-authority.
- Decision добавляет production/test/runtime LOC `0`, создаёт только свою card,
  same-slug OpenSpec artifacts, synchronized release-CI spec и archive metadata;
  authorization/implementation v9 и certification остаются отсутствующими.
- History, real full baseline, affected execution/benchmark, live matrix и
  certification checks не запускаются и не принимаются.

## Change Set
- `rescue-affected-release-profile-direct-investigation-dependency-boundary-v9`

## Verify
- GREEN required: exact base/remote binding, terminal-v8 chronology and
  forensic boundary, contradiction and no-bypass rule, exact six-field v9
  authorization, direct rescue dependency in future implementation, preserved
  affected floor, successor absence, strict OpenSpec, JSON/TOML, source
  classification, current-only public scan, archive/main sync, whitespace,
  manifest scope and ordinary/high preflight.
- GREEN retained: `safe-base-contract-v9` and
  `docs-contract-green-v9-prearchive` plus
  `post-archive-contract-scope-v9` prove exact base/remote and successor
  absence, strict/config/classification/current-public/whitespace gates, exact
  archive/main equality, clean manifest scope and docs-only
  production/test/runtime LOC `0`.
- RED: not applicable; this docs-only investigation/design adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live
  matrix, v9 successor creation/implementation, certification and terminal v8 reuse.

## Archive
- `openspec/changes/archive/2026-08-27-rescue-affected-release-profile-direct-investigation-dependency-boundary-v9/`

## Related
- `openspec/changes/archive/2026-08-27-rescue-affected-release-profile-direct-investigation-dependency-boundary-v9/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v8.md`
- `openspec/board/4.done/investigate-affected-release-profile-contract-closure-boundary-v8.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: one docs-only investigation/design decision is synchronized and
archived. Terminal v8 remains forensic-only; exact directly bound v9 lineage is
review-ready while successors and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-affected-release-profile-direct-investigation-dependency-boundary-v9`

### Why
Published v8 made its implementation dependency set exact without the
investigation id that generic preflight requires directly, so executable v8
cannot pass both contracts and must remain terminal.

### Goal
Publish one docs-only decision that supersedes executable v8 with a clean v9
lineage whose implementation directly depends on this investigation.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact contradiction, terminal chronology, v9 order and authorization object,
  direct-investigation dependency, preserved release floor, LOC, dormancy and
  prohibited-suite boundaries above are synchronized.

### Depends On
- `investigate-affected-release-profile-contract-closure-boundary-v8`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v7`
- `authorize-bounded-affected-release-profile-v8`

### Related
- `openspec/changes/archive/2026-08-27-rescue-affected-release-profile-direct-investigation-dependency-boundary-v9/`

## Log
- 2026-08-27 created in a clean worktree and remote branch from exact safe v8
  authorization tip; unpublished v8 payload/evidence were not read or imported.
- 2026-08-27 FF produced one apply-ready docs-only investigation/design change;
  v9 successors, executable LOC and prohibited evidence remain absent.
- 2026-08-27 DO synchronized four release-CI requirements, archived the
  same-slug change and passed strict/config/classification/current-public/
  whitespace checks with production/test/runtime LOC `0`; prohibited
  execution and v9 successors remained absent.
- 2026-08-27 initial archive command detected the already-synchronized delta
  and changed nothing; the documented `--skip-specs` retry archived the exact
  idempotently synced payload.
- 2026-08-27 final post-archive evidence passed with no active OpenSpec changes,
  exact archive/main equality and only the seven card-owned committable paths.
- 2026-08-27T17:03:49Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
