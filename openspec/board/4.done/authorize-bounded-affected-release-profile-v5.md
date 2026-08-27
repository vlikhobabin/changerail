# Авторизовать bounded affected release profile v5

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 14

## Source
- Published decision `rescue-affected-release-profile-red-evidence-boundary`,
  commit `ab23b7c8cfafd1b031b669a9a07667e135efd603`.
- Published integration decision, semantic scheduler v1 and affected v4
  authorization.
- Terminal unpublished affected v4 implementation remains forensic-only and
  cannot satisfy this authorization or its successor.

## Summary
Авторизовать ровно один clean implementation successor для affected profile v5
в пределах auditable pre-production RED boundary и `<=499` production LOC.

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
- `rescue-affected-release-profile-red-evidence-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v4`

## Blocks
- `implement-bounded-affected-release-profile-v5`

## Authorization
- Investigation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md","investigation_id":"rescue-affected-release-profile-red-evidence-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v5.md","successor_id":"implement-bounded-affected-release-profile-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Authorization публикуется docs-only от exact rescue HEAD `ab23b7c…` и
  содержит ровно один six-field object выше без дополнительных полей/объектов.
- `Depends On` содержит ровно rescue decision, integration decision, scheduler
  v1 и affected v4 authorization; `Blocks` содержит только exact v5
  implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md","authorization_id":"authorize-bounded-affected-release-profile-v5"}`,
  начинается от authorization-publishing HEAD, добавляет не более 499
  production LOC, зависит ровно от четырех predecessors выше плюс эту
  authorization и блокирует только `certify-accelerated-release-loop-v1`.
- До первой production, CI или main-spec mutation future v5 содержит только
  card, same-slug OpenSpec и focused-test artifacts и запускает настоящий
  failing test через `bin/changerail-evidence capture`.
- Captured command сначала печатает результат
  `bin/changerail-review-verdict fingerprint --workspace .`, затем запускает
  focused test и сохраняет его non-zero status; wrapper с exit `0`, note или
  поздняя reproduction не удовлетворяют RED boundary.
- Retained entry имеет `status: failed`, non-zero `exit_code`, а raw output
  содержит pre-production `tree_sha`, `diff_fingerprint` и конкретную ошибку
  отсутствующего production symbol или module.
- Fresh reviewer восстанавливает сохранённый tree object, сравнивает его с
  authorization HEAD и fail-closed подтверждает отсутствие production, CI и
  main-spec mutations до RED; missing object или forbidden path дают `NO-GO`.
- Future v5 сохраняет exact 35→30 profile, aggregate admission, strict bounded
  four-stream selector, typed scheduler rows/jobs, full-only authority, exact
  source-safe four-step CI, connected resolved-base guards и protocol-artifact
  non-authority из published v4 sources.
- Terminal v4 code, card, manifest, verdicts, logs и evidence не читаются, не
  копируются, не cherry-pick-ятся и не принимаются ни одним future gate.
- Authorization добавляет production/test/runtime LOC 0, не создаёт successor,
  code, dependency, schema, CI или runtime authority.
- History/full/affected execution/benchmark/live/certification/prototype
  evidence не запускается и не принимается; требуется fresh Sol/high review.

## Change Set
- `authorize-bounded-affected-release-profile-v5`

## Verify
- GREEN required: exact source object/reference/dependencies/sole block/LOC,
  published rescue reachability, RED capture/reconstruction boundary, preserved
  v4 floor, successor absence, strict OpenSpec, JSON/TOML, source
  classification, current public scan, archive/main sync, whitespace, manifest
  scope and ordinary/high preflight.
- Retained mandatory publication evidence will bind exact `ab23b7c...` to the
  expected remote authorization branch under ignored runtime state.
- RED: not applicable; docs-only authorization adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live matrix,
  successor creation/implementation, certification, commit or push before review.

## Archive
- `openspec/changes/archive/2026-08-27-authorize-bounded-affected-release-profile-v5/`

## Related
- `openspec/changes/authorize-bounded-affected-release-profile-v5/`
- `openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO complete: exact docs-only v5 authorization is synchronized and archived.
Implementation successor, focused tests and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-affected-release-profile-v5`

### Why
Published rescue requires a separately reviewed and published authorization
before any v5 implementation card, test or executable work may exist.

### Goal
Publish one exact bounded authorization for the sole clean v5 implementation.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact source object, future reference, dependencies, sole block, retained RED
  boundary, published v4 floor, LOC and dormancy contracts are machine-checkable.

### Depends On
- `rescue-affected-release-profile-red-evidence-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v4`

### Related
- `openspec/changes/authorize-bounded-affected-release-profile-v5/`

## Log
- 2026-08-27 created in a clean worktree from exact published rescue HEAD;
  successor and terminal v4 payload/evidence were not created, read or imported.
- 2026-08-27 FF produced one exact apply-ready docs-only authorization change;
  successor, executable LOC and prohibited evidence remain absent.
- 2026-08-27 DO retained exact source publication evidence, synchronized
  release-CI, archived the change and prepared ordinary/high preflight.
- 2026-08-27T05:12:05Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
