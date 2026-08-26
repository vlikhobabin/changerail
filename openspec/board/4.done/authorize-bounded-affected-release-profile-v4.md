# Авторизовать bounded affected release profile v4

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 12

## Source
- Published decision `rescue-affected-release-profile-proof-connectivity-boundary`,
  commit `63be8754ed6deb474d1c91dab3e931d28e7f37d3`.
- Published integration decision and semantic scheduler v1 implementation.
- Published affected v3 authorization; its unpublished implementation successor
  is exhausted by the source decision and remains forensic-only.

## Summary
Авторизовать ровно один clean implementation successor для affected profile v4
в пределах proof-connectivity boundary и `<=499` production LOC.

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
- `rescue-affected-release-profile-proof-connectivity-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v3`

## Blocks
- `implement-bounded-affected-release-profile-v4`

## Authorization
- Investigation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md","investigation_id":"rescue-affected-release-profile-proof-connectivity-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v4.md","successor_id":"implement-bounded-affected-release-profile-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Authorization публикуется docs-only от exact decision HEAD `63be875…` и
  содержит ровно один six-field object выше без дополнительных полей/объектов.
- `Depends On` содержит ровно decision, integration decision, scheduler v1 и
  affected v3 authorization; `Blocks` содержит только exact v4 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md","authorization_id":"authorize-bounded-affected-release-profile-v4"}`,
  начинается от authorization-publishing HEAD и добавляет не более 499
  production LOC.
- Future implementation зависит ровно от четырех published predecessors выше
  плюс эту published authorization и блокирует только
  `certify-accelerated-release-loop-v1`.
- Resolved-base proof достигает и независимо мутирует error, return code,
  stderr, timeout, exact newline framing, 40/64 lowercase-hex OID и
  non-ancestor; удаление каждого guard обязано сделать focused gate красным.
- Protocol proof начинает с affected subset/fallback, admission failure,
  scheduler failure и malformed summary; add/forge/replay receipt, capture,
  marker или cache не могут повысить authority или изменить control report.
- Future v4 сохраняет exact 35→30 profile, aggregate admission, strict selector,
  typed scheduler rows/jobs, full-only authority и exact source-safe four-step CI.
- Future v4 строится clean из published sources; terminal unpublished v3 code,
  cards, manifests, verdicts, logs и evidence запрещены.
- Authorization добавляет production/test/runtime LOC 0, не создаёт successor,
  code, dependency, schema, CI или runtime authority.
- History/full/affected execution/benchmark/live/certification/prototype evidence
  не запускается и не принимается; требуется один fresh Sol/high review.

## Change Set
- `authorize-bounded-affected-release-profile-v4`

## Verify
- GREEN required: exact object/reference/dependencies/sole block/LOC, published
  decision reachability, proof-connectivity preservation, successor absence,
  strict OpenSpec, JSON/TOML, classification, current public scan,
  archive/main sync, whitespace, manifest scope and preflight.
- Retained mandatory publication evidence:
  `.runtime/changerail/evidence/authorize-bounded-affected-release-profile-v4/index.json`
  binds exact source commit to the expected rescue branch.
- RED: not applicable; docs-only authorization adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live matrix,
  successor creation/implementation, certification, commit or push before review.

## Archive
- `openspec/changes/archive/2026-08-26-authorize-bounded-affected-release-profile-v4/`

## Related
- `openspec/changes/authorize-bounded-affected-release-profile-v4/`
- `openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO complete: exact docs-only v4 authorization is synchronized and archived.
Successor and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-affected-release-profile-v4`

### Why
Published rescue requires a separately reviewed and published authorization
before any v4 implementation card or executable work may exist.

### Goal
Publish one exact bounded authorization for the sole clean v4 implementation.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact source object, future reference, dependencies, sole block,
  proof-connectivity boundary, LOC and dormancy contracts are machine-checkable.

### Depends On
- `rescue-affected-release-profile-proof-connectivity-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v3`

### Related
- `openspec/changes/authorize-bounded-affected-release-profile-v4/`

## Log
- 2026-08-26 created in a clean worktree from exact published rescue HEAD;
  successor and unpublished v3 payload/evidence were not created or imported.
- 2026-08-26 FF produced one exact apply-ready docs-only authorization change.
- 2026-08-26 DO retained exact source publication evidence, synchronized
  release-CI, archived the change and prepared ordinary/high preflight.
- 2026-08-26T19:12:11Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
