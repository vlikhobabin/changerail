# Авторизовать psutil-backed release child supervisor v2

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R10-S2A

## Source
- Exact published decision `rescue-psutil-release-child-supervisor-boundary`,
  commit `d1ece95903f4b68b44d52f14951afce7c345cdb5`.
- The published S v1 authorization has one successor only and cannot authorize
  v2. Failed unpublished authorization material is not reusable.

## Summary
Опубликовать единственный bounded authorization source для будущего
psutil-backed S2 child supervisor, сохранив exact decision lineage, portable
cleanup contract и structural dormancy без создания successor card или code.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: docs-only deterministic
- Independent review: fresh `gpt-5.6-sol`/`high` pending
- Same-card repair/rescue budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `rescue-psutil-release-child-supervisor-boundary` (published
  `d1ece95903f4b68b44d52f14951afce7c345cdb5`)

## Blocks
- `implement-psutil-backed-release-child-supervisor-v2`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- This authorization depends on the published decision and blocks only exact
  `implement-psutil-backed-release-child-supervisor-v2`; the decision blocks
  both this authorization and that implementation.
- The future implementation depends on both decision and authorization, uses
  only `{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}`
  as its published authorization reference, and remains at `<=499` added
  production LOC relative to the exact authorization-publishing HEAD.
- Future S2 pins `psutil==7.1.0` in runtime, development, bootstrap and
  admission surfaces; it uses only a bounded stdlib `selectors`/`prctl`
  adapter and must not require, write or derive authority from a writable
  cgroup.
- Future S2 has distinct positive `execution_timeout` and `cleanup_timeout`,
  total elapsed time at most `execution_timeout + cleanup_timeout + 1.0s`, and
  terminal cleanup failure. Every psutil error fails closed; process identity
  is exact `(pid, create_time)`.
- The inclusive maxima are 128 unique identities, 128 descendants per
  `children(recursive=True)` scan and 32 cleanup scans. Only strict excess is
  terminal. Cleanup succeeds only on the second consecutive empty identity
  scan; zero or one empty scan cannot report success.
- Release baseline, CI, review/publish gates, receipt schema and production
  entrypoint remain dormant. H4/I3/W1/R3/A3 authorization and implementation
  remain blocked until S2 publication and a later tracked refresh.
- This docs-only payload adds production, test and runtime LOC `0`; successor
  card/code remain absent. It does not use history, full baseline, live
  execution, review, commit or push evidence.

## Change Set
- `authorize-psutil-backed-release-child-supervisor-v2`

## Verify
- GREEN: strict target, `changerail-release-ci` and all OpenSpec validation;
  exact object, reciprocal relation, future-reference/absence and contract
  oracle; `.mcp.json` JSON and `.codex/config.toml` TOML parsing.
- GREEN: current-only public-surface scan, source classification, tracked and
  explicit-untracked whitespace, manifest validation/scope and normalized
  ordinary/high preflight after archive.
- This docs-only delivery ran no history scan, full release baseline, live
  execution, successor, review, commit or push.

## Archive
- `openspec/changes/archive/2026-08-25-authorize-psutil-backed-release-child-supervisor-v2/`

## Related
- `openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md`
- `openspec/changes/archive/2026-08-25-rescue-psutil-release-child-supervisor-boundary/`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO завершен: exact six-field authorization source, reciprocal lineage, future
two-field reference, bounded psutil S2 contract and dormant downstream refresh
gate synchronized in `changerail-release-ci`; the same-slug docs-only change
is archived. Production/test/runtime LOC: `0`. Future successor card/code and
downstream authorization or implementation work remain absent. Payload готов
к fresh independent ordinary review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-psutil-backed-release-child-supervisor-v2`

### Why
Published decision fixes a new S2 boundary, but a future implementation needs
one separately published, one-successor authorization source before it exists.

### Goal
Publish the exact authorization, portable cleanup contract and dormancy gate
for future S2 without creating or implementing its successor.

### Scope
- This card, same-slug OpenSpec artifacts, synchronized release-CI spec and
  archive metadata only; production/test/runtime LOC `0`.

### Acceptance
- Exact six-field object, reciprocal decision/authorization/future
  implementation dependencies, exact two-field future reference and `<=499`
  authorization-HEAD limit are retained.
- The psutil four-surface pin, portable adapter/no-cgroup, deadline, identity,
  inclusive cap, stable-empty and dormant downstream contracts are complete.
- Successor card/code and all downstream authorization or implementation work
  remain absent.

### Depends On
- `rescue-psutil-release-child-supervisor-boundary`

### Related
- `openspec/changes/authorize-psutil-backed-release-child-supervisor-v2/`

## Log
- 2026-08-25 FF created one same-slug docs-only authorization from the exact
  published S2 decision; future successor remains absent.
- 2026-08-25 DO synchronized `changerail-release-ci`, archived only this
  same-slug docs-only change and completed strict/current verification. No
  history/full/live execution, successor, review, commit or push occurred.
- 2026-08-25T22:40:43Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
