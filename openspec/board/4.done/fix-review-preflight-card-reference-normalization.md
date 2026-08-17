# Исправить нормализацию card reference в review preflight

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Root preflight evidence: published investigation `Blocks` stores a canonical
  successor filename, but the deterministic gate compares only a bare id.

## Summary
Нормализовать exact backticked card reference к id только для bare id,
`<id>.md` и canonical board path с финальным `<id>.md`; foreign stem и
ambiguous value остаются fail-closed.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Acceptance
- Valid bare id, filename and canonical board path satisfy only their exact
  expected card id.
- Foreign filename stems, non-board paths and ambiguous references do not
  satisfy the relation.
- Focused smoke covers valid `.md` and board-path references plus mismatches.

## Change Set
- `fix-review-preflight-card-reference-normalization`

## Verify
- `python3 scripts/smoke-review-preflight.py`: PASS.
- `python3 scripts/smoke-contract-schemas.py`: PASS, 20 schemas.
- `ruff check scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py scripts/smoke-contract-schemas.py`: PASS.
- `python3 -m py_compile scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py scripts/smoke-contract-schemas.py`: PASS.
- `openspec validate fix-review-preflight-card-reference-normalization --strict` and
  `openspec validate --all --strict`: PASS.
- `python3 scripts/public-surface-scan.py`: PASS.
- `git diff --check`: PASS.
- `python3 scripts/run-release-baseline.py`: PASS, 34/34 steps.

## Archive
- `openspec/changes/archive/2026-08-17-fix-review-preflight-card-reference-normalization/`

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `openspec/changes/archive/2026-08-17-fix-review-preflight-card-reference-normalization/`

## Result
Implementation is complete; the exact payload awaits one fresh independent
ordinary `high` review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `fix-review-preflight-card-reference-normalization`

### Why
Published board cards conventionally use backticked filenames, while the new
authorization relationship check expects a bare card id.

### Goal
Accept only exact equivalent card-reference forms without making the relation
check a fuzzy substring match.

### Scope
- Change the deterministic reference matcher and focused smoke fixture.
- Update the preflight contract requirement only where the accepted forms need
  to be stated.

### Acceptance
- `<id>`, `<id>.md` and canonical `openspec/board/<lane>/<id>.md` normalize to
  `<id>`.
- Other stems and noncanonical paths remain non-matches.

### Depends On
- `fix-review-preflight-investigation-authorization`

### Related
- `openspec/changes/fix-review-preflight-card-reference-normalization/`

## Log
- 2026-08-17T00:00:00Z targeted compatibility follow-up created from root
  preflight evidence.
- 2026-08-17T00:05:00Z one apply-ready change passed strict OpenSpec validation.
- 2026-08-17T00:15:00Z implementation, focused smoke and the 34-step release
  baseline passed; payload awaits its single independent ordinary review.
- 2026-08-17T00:20:00Z contract synced and change archived; card remains in
  `3.inprogress` for one fresh ordinary review.
- 2026-08-17T08:36:57Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
