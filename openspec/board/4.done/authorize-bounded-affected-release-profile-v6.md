# Авторизовать bounded affected release profile v6

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 16

## Source
- Published admission/bounds investigation decision
  `rescue-affected-release-profile-admission-bounds-boundary-v6`, exact commit
  `5d6bfe14b498d22f58be303283537c16cd450c07`.
- Published integration decision, semantic scheduler v1 and affected v5
  authorization.
- Terminal unpublished affected v5 implementation remains forensic-only and
  cannot satisfy this authorization or its successor.

## Summary
Авторизовать ровно один clean implementation successor для affected profile v6
с pre-mutation runtime-output admission, complete connected selector-bound
proof и `<=499` production LOC.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `rescue-affected-release-profile-admission-bounds-boundary-v6`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v5`

## Blocks
- `implement-bounded-affected-release-profile-v6`

## Authorization
- Investigation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md","investigation_id":"rescue-affected-release-profile-admission-bounds-boundary-v6","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v6.md","successor_id":"implement-bounded-affected-release-profile-v6","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Authorization публикуется docs-only от exact investigation HEAD
  `5d6bfe14...` и содержит ровно один six-field object выше без дополнительных
  полей, объектов, wrappers или reordered fields.
- `Depends On` содержит ровно investigation decision, integration decision,
  scheduler v1 implementation и affected v5 authorization; `Blocks` содержит
  только exact v6 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v6.md","authorization_id":"authorize-bounded-affected-release-profile-v6"}`,
  начинается от authorization-publishing HEAD, добавляет не более 499
  production LOC, зависит ровно от четырех predecessors выше плюс эту
  authorization и блокирует только `certify-accelerated-release-loop-v1`.
- До первой production, CI или main-spec mutation future v6 содержит только
  implementation card, same-slug OpenSpec и focused-test artifacts и напрямую
  запускает настоящий failing focused test через `bin/changerail-evidence capture`.
- Captured RED command сначала печатает
  `bin/changerail-review-verdict fingerprint --workspace .`, затем запускает
  focused test с настоящим non-zero exit; retained entry сохраняет failed
  status, non-zero exit, `tree_sha`, `diff_fingerprint` и missing production
  module или symbol, а saved tree существует до production mutation.
- Fresh reviewer восстанавливает saved RED tree относительно authorization
  HEAD и fail-closed подтверждает отсутствие production, CI и main-spec
  mutations; поздняя reproduction не удовлетворяет chronology boundary.
- Aggregate admission до selection, semantics и filesystem mutation проверяет
  runtime-output target и fail closed выдаёт bounded report с
  `semantic_started: 0` для existing file, symlink, wrong type, root escape,
  inaccessible или uncertain parent без uncaught pre-report exception.
- Focused proof содержит connected non-noop guard mutants для `MAX_PATH`,
  aggregate/deduplicated `MAX_PATHS`, каждого committed/staged/unstaged/
  untracked `MAX_GIT_BYTES`, aggregate four-stream bytes и runtime-output
  filesystem/admission ordering/type faults.
- Future v6 сохраняет exact 35→30 profile, aggregate admission, strict bounded
  four-stream selector, typed scheduler rows/jobs, full-only authority, exact
  source-safe four-step CI, connected resolved-base guards и protocol-artifact
  non-authority из published sources.
- Terminal unpublished v5 code, card, manifest, verdicts, logs и evidence не
  читаются, не копируются, не cherry-pick-ятся и не принимаются ни одним gate.
- Authorization добавляет production/test/runtime LOC 0, не создаёт successor,
  code, dependency, schema, CI или runtime authority.
- History/full/affected execution/benchmark/live/certification evidence не
  запускается и не принимается; требуется fresh Sol/high review.

## Change Set
- `authorize-bounded-affected-release-profile-v6`

## Verify
- GREEN required: exact published source/remote branch/object/reference/
  dependencies/sole block/LOC, successor absence, RED chronology and
  reconstruction boundary, runtime-output admission contract, complete
  selector-bound mutant inventory, preserved v5 floor, strict OpenSpec,
  JSON/TOML, source classification, current-only public scan, archive/main
  sync, whitespace, manifest scope and ordinary/high preflight.
- GREEN retained: `safe-base-remote-binding`, `lineage-successor-absence` and
  `post-archive-contract-scope` bind the exact source/remote, authorization
  shape, successor absence, archived delta/main sync and docs-only zero-LOC
  scope under ignored runtime evidence.
- RED: not applicable; docs-only authorization adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live
  matrix, successor creation/implementation, certification and prototype reuse.

## Archive
- `openspec/changes/archive/2026-08-27-authorize-bounded-affected-release-profile-v6/`

## Related
- `openspec/changes/authorize-bounded-affected-release-profile-v6/`
- `openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: one exact docs-only v6 authorization is synchronized and archived.
Implementation successor, focused tests and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-affected-release-profile-v6`

### Why
Published v6 investigation requires a separately reviewed and published
authorization before any v6 implementation card, test or executable work may
exist.

### Goal
Publish one exact bounded authorization for the sole clean v6 implementation.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact source object, future reference, dependencies, sole block, retained RED
  boundary, runtime-output admission, selector-bound proof, published floor,
  LOC and dormancy contracts are machine-checkable.

### Depends On
- `rescue-affected-release-profile-admission-bounds-boundary-v6`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v5`

### Related
- `openspec/changes/authorize-bounded-affected-release-profile-v6/`

## Log
- 2026-08-27 created in a clean worktree and remote branch from exact published
  v6 investigation HEAD; successor and terminal v5 forensic payload/evidence
  were not created, read or imported.
- 2026-08-27 FF produced one exact apply-ready docs-only authorization change;
  successor, executable LOC and prohibited evidence remain absent.
- 2026-08-27 DO retained exact source/remote and lineage/absence evidence,
  synchronized five release-CI requirements, archived the same-slug change and
  passed strict/config/classification/current-public/whitespace checks with
  production/test/runtime LOC `0`; prohibited execution remained absent.
- 2026-08-27T08:25:06Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
