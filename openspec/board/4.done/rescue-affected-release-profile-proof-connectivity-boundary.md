# Перезапустить affected profile через proof-connectivity boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 11S

## Source
- Published affected v3 authorization, exact tip
  `4203d1df3cdbe8b9f62bc6f30208b18d6860732e`.
- Published exact target/proof decision, integration decision and semantic scheduler v1.
- Unpublished `implement-bounded-affected-release-profile-v3` payload is terminal
  `NO-GO`, forensic-only and MUST NOT satisfy any future gate.

## Summary
Разрешить одну clean affected v4 lineage, в которой resolved-base guards и
отсутствие protocol-artifact authority доказаны связанными counterfactual
mutation fixtures до финальной certification.

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
- `rescue-affected-release-profile-exact-target-proof-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v3`

## Blocks
- `authorize-bounded-affected-release-profile-v4`
- `implement-bounded-affected-release-profile-v4`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v4 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md","investigation_id":"rescue-affected-release-profile-proof-connectivity-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v4.md","successor_id":"implement-bounded-affected-release-profile-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision публикуется docs-only от exact published v3 authorization tip,
  сохраняет published history и после публикации исчерпывает v3 implementation
  successor; failed v3 payload/evidence остаются forensic-only.
- Единственный future order: эта decision, docs-only
  `authorize-bounded-affected-release-profile-v4`, clean
  `implement-bounded-affected-release-profile-v4`, затем certification.
- Future authorization содержит ровно один exact six-field object выше,
  зависит ровно от этой decision, integration decision, scheduler v1 и v3
  authorization и блокирует только v4 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md","authorization_id":"authorize-bounded-affected-release-profile-v4"}`,
  зависит от этих четырех predecessors и v4 authorization, блокирует только
  certification, начинается от authorization-publishing HEAD и добавляет не
  более 499 production LOC.
- Resolved-base proof отдельно достигает и мутирует spawn/error, return code,
  stderr, timeout, exact single-newline framing, 40/64-byte lowercase hex OID,
  uppercase/non-hex/short/long/multiple/missing-newline и non-ancestor guards;
  удаление или ослабление каждого guard обязано сделать focused gate красным.
- Protocol proof начинает с non-authoritative affected subset, affected full
  fallback, admission failure, scheduler failure и malformed summary; add,
  forge и replay receipt/capture/marker/cache не могут повысить authority,
  изменить report или создать accepted protocol state.
- Сохраняются уже закрытые v3 boundaries: exact 35→30 profile, aggregate
  admission, strict four-stream selector, typed scheduler rows/jobs, full-only
  authority и exact source-safe four-step CI.
- Решение добавляет production/test/runtime LOC 0, не создаёт successors и не
  запускает history/full/affected benchmark/live/certification evidence.

## Change Set
- `rescue-affected-release-profile-proof-connectivity-boundary`

## Verify
- GREEN required: exact lineage/object/reference/order, v3 exhaustion,
  connected resolved-base and protocol non-authority boundaries, strict
  OpenSpec, JSON/TOML, current public scan, classification, whitespace,
  successor absence, archive/main sync, manifest scope and preflight.
- Retained mandatory publication evidence:
  `.runtime/changerail/evidence/rescue-affected-release-profile-proof-connectivity-boundary/index.json`
  binds exact `4203d1d...` to the expected remote authorization branch.
- RED: not applicable; docs-only decision adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live matrix,
  successor creation/implementation, certification, commit or push before review.

## Archive
- `openspec/changes/archive/2026-08-26-rescue-affected-release-profile-proof-connectivity-boundary/`

## Related
- `openspec/changes/rescue-affected-release-profile-proof-connectivity-boundary/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v3.md`
- `openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO complete: one docs-only decision is synchronized and archived. Exact v4
lineage and proof-connectivity boundary are review-ready; successor code and
prohibited evidence remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-affected-release-profile-proof-connectivity-boundary`

### Why
Affected v3 exhausted its sole repair while two mutation oracles remained
disconnected; continuing that implementation would bypass review lifecycle.

### Goal
Publish one clean, exact and exclusive affected v4 proof-connectivity decision.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact lineage, connected resolved-base/protocol proof, preserved v3 floor,
  LOC, dormancy and prohibited-suite boundaries above are synchronized.

### Depends On
- `rescue-affected-release-profile-exact-target-proof-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v3`

### Related
- `openspec/changes/rescue-affected-release-profile-proof-connectivity-boundary/`

## Log
- 2026-08-26 created in a clean worktree from exact published v3 authorization
  tip; no unpublished v3 payload or evidence was imported.
- 2026-08-26 FF produced one apply-ready docs-only change; successors,
  executable LOC and prohibited evidence remain absent.
- 2026-08-26 DO synchronized release-CI, archived the same-slug change and
  prepared the docs-only payload for independent Sol/high review.
- 2026-08-26T18:48:22Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
