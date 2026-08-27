# Перезапустить affected profile через RED-evidence boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 13S

## Source
- Published affected v4 authorization, exact tip
  `3e85ce1de7e8b6f9bb60a04b924838e24064dd5b`.
- Published integration decision, semantic scheduler v1 and affected v4
  authorization.
- Unpublished `implement-bounded-affected-release-profile-v4` payload ended in
  terminal review-cycle-2 `NO-GO`; its repair budget is exhausted and all of
  its code, card, manifest, verdicts, logs and evidence are forensic-only.

## Summary
Разрешить одну clean affected v5 lineage, в которой test-first chronology
доказывается сохранённым machine-auditable RED evidence до первой production
mutation, а terminal v4 ничего не передаёт будущей реализации.

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
- `authorize-bounded-affected-release-profile-v4`

## Blocks
- `authorize-bounded-affected-release-profile-v5`
- `implement-bounded-affected-release-profile-v5`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v5 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md","investigation_id":"rescue-affected-release-profile-red-evidence-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v5.md","successor_id":"implement-bounded-affected-release-profile-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision публикуется docs-only от exact published v4 authorization tip,
  сохраняет published history и после публикации исчерпывает v4 implementation;
  весь unpublished v4 payload остаётся terminal forensic-only и не читается,
  не копируется, не cherry-pick-ится и не удовлетворяет future gate.
- Единственный future order: эта decision, docs-only
  `authorize-bounded-affected-release-profile-v5`, clean
  `implement-bounded-affected-release-profile-v5`, затем certification.
- Future authorization содержит ровно один exact six-field object выше,
  зависит ровно от этой decision, integration decision, scheduler v1 и v4
  authorization и блокирует только v5 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md","authorization_id":"authorize-bounded-affected-release-profile-v5"}`,
  зависит от этих четырёх predecessors плюс authorization v5, блокирует только
  certification, начинается от authorization-publishing HEAD и добавляет не
  более 499 production LOC.
- До первой future v5 production mutation разрешены только card, same-slug
  OpenSpec и focused-test artifacts; затем delivery запускает настоящий
  failing focused test только через `bin/changerail-evidence capture`.
- Captured command сначала выполняет
  `bin/changerail-review-verdict fingerprint --workspace .`, затем тот же
  focused test, который завершается non-zero из-за конкретного отсутствующего
  production symbol или module; wrapper с итоговым exit `0` запрещён.
- Retained RED entry имеет `status: failed`, non-zero `exit_code` и raw output
  с pre-production `tree_sha`, `diff_fingerprint` и конкретной missing-symbol
  или missing-module ошибкой. Поздняя reproduction не заменяет этот entry.
- Fresh reviewer восстанавливает сохранённый pre-production tree object,
  сравнивает его с authorization HEAD и подтверждает отсутствие production,
  CI и main-spec mutations; test/card/OpenSpec additions не считаются
  production mutation.
- Future v5 сохраняет все опубликованные v4 boundaries: exact 35→30 profile,
  aggregate admission, strict four-stream selector, typed scheduler rows/jobs,
  full-only authority, exact source-safe four-step CI, connected resolved-base
  guards и protocol-artifact non-authority.
- Решение добавляет production/test/runtime LOC 0, не создаёт successors и не
  запускает history/full/affected benchmark/live/certification evidence.

## Change Set
- `rescue-affected-release-profile-red-evidence-boundary`

## Verify
- GREEN required: exact lineage/object/reference/order/absence, v4 exhaustion,
  RED capture/reviewer boundary, preserved published v4 floor, strict OpenSpec,
  JSON/TOML, current public scan, source classification, whitespace,
  archive/main sync, manifest scope and ordinary/high preflight.
- Retained mandatory publication evidence will bind exact `3e85ce1...` to the
  expected remote rescue branch under ignored runtime state.
- RED: not applicable; this docs-only decision adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live matrix,
  successor creation/implementation, certification, commit or push before review.

## Archive
- `openspec/changes/archive/2026-08-27-rescue-affected-release-profile-red-evidence-boundary/`

## Related
- `openspec/changes/rescue-affected-release-profile-red-evidence-boundary/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO complete: one docs-only decision is synchronized and archived. Exact v5
lineage and retained RED chronology boundary are review-ready; successor code
and prohibited evidence remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-affected-release-profile-red-evidence-boundary`

### Why
Affected v4 exhausted its only repair because the real pre-production RED run
was not retained when it occurred; a later reproduction cannot prove test-first
chronology.

### Goal
Publish one clean, exact and exclusive affected v5 lineage with a retained,
machine-auditable pre-production RED boundary.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact lineage, RED evidence ordering and reviewer reconstruction, preserved
  v4 proof floor, LOC, dormancy and prohibited-suite boundaries above are
  synchronized.

### Depends On
- `rescue-affected-release-profile-proof-connectivity-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v4`

### Related
- `openspec/changes/rescue-affected-release-profile-red-evidence-boundary/`

## Log
- 2026-08-27 created in a clean worktree from exact published v4 authorization
  tip; no unpublished v4 payload or evidence was read, imported or executed.
- 2026-08-27 FF produced one apply-ready docs-only rescue change; successor,
  executable LOC and prohibited evidence remain absent.
- 2026-08-27 DO retained exact source publication evidence, synchronized
  release-CI, archived the change and prepared ordinary/high preflight.
- 2026-08-27T04:47:15Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
