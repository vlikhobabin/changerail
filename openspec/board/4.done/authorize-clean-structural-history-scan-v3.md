# Авторизовать clean structural history scan v3

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R9-H

## Source
- Published clean-lineage decision
  `rescue-private-release-loop-acceleration-publication-boundary`, commit
  `25c76e7b4ae60d87598077935f829f43a5808330`.

## Summary
Опубликовать docs-only authorization source для единственного будущего clean
structural history scan v3 без новой authority или wire protocol.

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
- `rescue-private-release-loop-acceleration-publication-boundary`

## Blocks
- `deliver-clean-structural-history-scan-v3`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/deliver-clean-structural-history-scan-v3.md","successor_id":"deliver-clean-structural-history-scan-v3","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}`

## Acceptance
- Ровно один schema-valid six-field authorization object совпадает с exact
  published decision и future `3.inprogress` successor path/id.
- Decision `Blocks`, authorization `Depends On`/`Blocks` и future successor
  `Depends On` образуют exact reciprocal lineage.
- Future successor создаётся только после publication этой authorization и
  использует в `Published investigation authorization` ровно inline JSON
  `{"authorization_card":"openspec/board/4.done/authorize-clean-structural-history-scan-v3.md","authorization_id":"authorize-clean-structural-history-scan-v3"}`.
- Authorization ceiling ровно `350`; implementation acceptance остаётся
  `<=349` production LOC относительно future published authorization HEAD.
- Protocol flag `false`; payload не добавляет authority, wire protocol,
  schema/parser/helper/runtime/CLI/test/production surfaces.
- H владеет только bounded structural history traversal, Git-compatible
  parsing, memoization, non-mutation и focused/CI history ownership proof;
  implementation card/code не создаются в этой карточке.

## Change Set
- `authorize-clean-structural-history-scan-v3`

## Verify
- Strict target/capability/all OpenSpec validation and exact authorization,
  lineage and future-reference assertions.
- JSON/TOML, current-only public scan, source classification, whitespace,
  delivery-manifest scope and normalized ordinary/high preflight.
- No reachable-history scan, full baseline, live run, successor, review,
  commit or push.

## Archive
- `openspec/changes/archive/2026-08-25-authorize-clean-structural-history-scan-v3/`

## Result
DO complete: the exact authorization source and release-CI contract were
synchronized and archived. Production, test and runtime additions remain `0`;
the future successor card/code remains absent. RED evidence is not applicable
because this is docs-only work.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Related
- `openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md`
- `openspec/changes/archive/2026-08-25-authorize-clean-structural-history-scan-v3/`
- `openspec/specs/changerail-release-ci/spec.md`

## Change 1: `authorize-clean-structural-history-scan-v3`

### Why
Future H implementation needs one clean published authorization source before
its successor card or code may exist.

### Goal
Bind the exact published decision and sole future successor through the
minimal six-field authorization object.

### Scope
- Board/OpenSpec/spec relationship docs only.
- Production/test/runtime LOC: 0.

### Acceptance
- The source contains one exact six-field object with ceiling `350` and
  protocol flag `false`.
- The reciprocal lineage and exact future two-field source reference are
  documented without creating the successor.
- H ownership stays limited to structural history traversal, Git-compatible
  parsing, memoization, non-mutation and focused/CI history proof.

### Depends On
- `rescue-private-release-loop-acceleration-publication-boundary`

### Related
- `openspec/changes/authorize-clean-structural-history-scan-v3/`

## Log
- 2026-08-25 authorization card created from exact published decision;
  implementation successor not yet created.
- 2026-08-25 FF prepared exactly one docs-only authorization change with
  proposal, design, `changerail-release-ci` delta and tasks; strict target/all
  OpenSpec validation passed without successor, history, full, live, review,
  commit or push work.
- 2026-08-25T19:08:13Z DO synchronized `changerail-release-ci`, archived the
  change and prepared the docs-only review handoff. Strict OpenSpec,
  JSON/TOML, exact authorization/lineage, current public scan, classification
  and whitespace checks passed; no history, full, live, successor, review,
  commit or push work ran.
- 2026-08-25T19:19:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
