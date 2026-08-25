# Авторизовать bounded structural public history scan

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R3-A

## Source
- Published investigation `investigate-structural-public-history-scan-proof`,
  commit `8adddfe`.

## Summary
Опубликовать docs-only authorization source, который связывает exact structural
investigation и единственный bounded implementation successor для repeated
defect lineage без нового protocol/authority.

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
- `investigate-structural-public-history-scan-proof`

## Blocks
- `deliver-structurally-bounded-public-history-scan`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-structural-public-history-scan-proof.md","investigation_id":"investigate-structural-public-history-scan-proof","successor_card":"openspec/board/3.inprogress/deliver-structurally-bounded-public-history-scan.md","successor_id":"deliver-structurally-bounded-public-history-scan","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`

## Acceptance
- Ровно один schema-valid six-field authorization object совпадает с exact
  published investigation и future `3.inprogress` successor path/id.
- Investigation `Blocks`, authorization `Depends On`/`Blocks` и successor
  `Depends On` образуют exact reciprocal lineage.
- Future successor создаётся только после publication этой
  authorization и использует в `Published investigation authorization`
  ровно inline JSON
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}`.
- Authorization ceiling ровно `301`; implementation acceptance остаётся
  `<=300` production LOC vs `ccccb625`.
- Protocol flag `false`; новых schema/parser/helper/runtime/CLI/test/production
  surfaces нет.
- Decision/spec relation docs могут быть дополнены только exact successor link;
  implementation card/code не создаются в этой карточке.

## Change Set
- `authorize-bounded-structural-public-history-scan`

## Verify
- GREEN: strict change, `changerail-release-ci` and all OpenSpec validation.
- GREEN: `.mcp.json` JSON and `.codex/config.toml` TOML parsing.
- GREEN: current-only public-surface scan and source classification.
- GREEN: tracked and explicit untracked whitespace checks.
- GREEN: delivery manifest validation/scope and normalized ordinary/high
  preflight after archival handoff.
- No history scan, benchmark or full baseline.

## Archive
- `openspec/changes/archive/2026-08-25-authorize-bounded-structural-public-history-scan/`

## Result
Delivery завершен: exact six-field authorization object и reciprocal lineage
сохранены, `changerail-release-ci` synchronized, а change archived. Production,
test и runtime additions remain `0` LOC; successor card/code не создавались.
Payload готов к independent ordinary review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Related
- `openspec/changes/authorize-bounded-structural-public-history-scan/`
- `openspec/changes/archive/2026-08-25-authorize-bounded-structural-public-history-scan/`
- `openspec/board/4.done/investigate-structural-public-history-scan-proof.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Change 1: `authorize-bounded-structural-public-history-scan`

### Why
Truthful repeated-defect successor должен пройти deterministic
investigation-required boundary через отдельный published authorization source.

### Goal
Связать exact investigation и successor минимальным six-field object.

### Scope
- Board/OpenSpec/spec relationship docs only.
- Production/test/runtime LOC: 0.

### Acceptance
- Authorization source содержит ровно один exact six-field object с
  ceiling `301` и protocol flag `false`.
- Investigation, authorization и future successor сохраняют exact
  reciprocal relations, а successor использует только exact
  two-field inline source reference.
- Successor card/code, production, tests, runtime state, history scan и
  baseline не создаются.

### Depends On
- `investigate-structural-public-history-scan-proof`

### Related
- `openspec/changes/authorize-bounded-structural-public-history-scan/`

## Log
- 2026-08-25T02:30:00Z authorization card created from published structural
  decision; implementation successor not yet created.
- 2026-08-25T02:33:25Z `$changerail-ff` prepared exactly one docs-only
  authorization change with proposal, design, `changerail-release-ci` delta
  and tasks; no successor card/code, production/test/runtime surface, history
  scan, benchmark or full baseline was created or run.
- 2026-08-25T02:39:20Z `$changerail-do` synchronized the release-CI contract,
  archived the docs-only change and moved the source to `3.inprogress` for
  independent ordinary review; production/test/runtime additions remain zero.
- 2026-08-25T02:46:38Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
