# Авторизовать bounded Git-compatible structural public history scan

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R4-A

## Source
- Published rescue investigation
  `rescue-git-commit-header-compatibility-decision`, commit `b7bd6f7`.

## Summary
Опубликовать docs-only authorization source, который связывает принятую
Git-compatible commit-header grammar и единственный чистый structural history
scan successor без нового protocol или authority.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Depends On
- `rescue-git-commit-header-compatibility-decision`

## Blocks
- `deliver-git-compatible-structural-public-history-scan-replacement`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/rescue-git-commit-header-compatibility-decision.md","investigation_id":"rescue-git-commit-header-compatibility-decision","successor_card":"openspec/board/3.inprogress/deliver-git-compatible-structural-public-history-scan-replacement.md","successor_id":"deliver-git-compatible-structural-public-history-scan-replacement","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`

## Acceptance
- Ровно один schema-valid six-field authorization object совпадает с exact
  published rescue investigation и future `3.inprogress` successor path/id.
- Investigation `Blocks`, authorization `Depends On`/`Blocks` и successor
  `Depends On` образуют exact reciprocal lineage.
- Future successor создаётся только после publication этой authorization и
  использует в `Published investigation authorization` ровно inline JSON
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-git-commit-header-compatible-history-scan.md","authorization_id":"authorize-bounded-git-commit-header-compatible-history-scan"}`.
- Authorization ceiling ровно `301`; implementation acceptance остаётся
  `<=300` production LOC относительно `ccccb625`.
- Protocol flag `false`; новых schema/parser/helper/runtime/CLI/test/production
  surfaces нет.
- Rescue decision/spec relation docs могут быть дополнены только exact
  successor link; implementation card/code не создаются в этой карточке.

## Change Set
- `authorize-bounded-git-commit-header-compatible-history-scan`

## Verify
- Strict target/capability/all OpenSpec validation and exact authorization parser.
- JSON/TOML, current-only public scan, classification, whitespace, manifest,
  scope and normalized ordinary/high preflight.
- No history scan, benchmark or full baseline.

## Result
Delivery complete. The exact authorization source and release-CI contract were
synced; `2026-08-25-authorize-bounded-git-commit-header-compatible-history-scan`
is archived. Production, tests and runtime additions remain zero, and the
future replacement card/code has not been created.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-git-commit-header-compatible-history-scan`

### Why
Repeated-defect replacement должен пройти deterministic investigation-required
boundary через отдельный published authorization source.

### Goal
Связать exact rescue investigation и successor минимальным six-field object.

### Scope
- Board/OpenSpec/spec relationship docs only.
- Production/test/runtime LOC: 0.

### Acceptance
- Authorization source содержит ровно один exact six-field object с ceiling
  `301` и protocol flag `false`.
- Investigation, authorization и future successor сохраняют exact reciprocal
  relations, а successor использует только exact two-field inline source ref.
- Successor card/code, production, tests, runtime state, history scan и baseline
  не создаются.

### Depends On
- `rescue-git-commit-header-compatibility-decision`

### Related
- `openspec/changes/authorize-bounded-git-commit-header-compatible-history-scan/`

## Log
- 2026-08-25T04:40:00Z authorization card created from published rescue
  decision; implementation successor not yet created.
- 2026-08-25T05:11:00Z FF prepared exactly one apply-ready docs-only
  authorization change; successor card/code, archive, review, commit, push,
  history scan, benchmark and full baseline were not run.
- 2026-08-25T05:16:00Z DO synchronized the exact release-CI authorization
  requirement, archived `2026-08-25-authorize-bounded-git-commit-header-compatible-history-scan`
  with `--skip-specs` after the explicit sync, and completed docs-only checks.
  Final normalized archived preflight is the remaining deterministic review
  handoff gate; history scan, benchmark, full baseline, review, commit and push
  were not run.
- 2026-08-25T05:21:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
