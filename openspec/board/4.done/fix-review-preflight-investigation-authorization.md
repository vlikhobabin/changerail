# Исправить authorization investigation в review preflight

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
- Follow-up к published risk-tiered review preflight: production LOC ошибочно
  учитывает Go `*_test.go`, а approved successor investigation не может
  машинно подтвердить ограниченное исключение для protocol и LOC.

## Summary
Сделать published-investigation authorization структурированным и
fail-closed: successor ссылается на чистый `HEAD`-tracked published source,
а source связывает точные investigation/successor card id и path. Investigation
`Blocks` successor, successor `Depends On` investigation; source владеет
ceiling не более 500 и protocol allowance. Go `*_test.go` не является
production LOC.

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
- Preflight excludes Go `*_test.go` from added production LOC without
  excluding production Go files.
- A successor can declare one inline JSON reference to a published authorization
  source; that source, not the successor, binds exact investigation/successor
  card ids, a bounded ceiling up to 500 and an explicit protocol allowance.
- Missing, unreadable, unpublished, stale or reciprocal-binding-mismatched
  authorization remains `investigation-required`; LOC above the authorized
  ceiling remains `investigation-required`.
- Focused adversarial smoke covers test-file exclusion, valid 500-line
  authorization, missing/stale/mismatched authority, protocol allowance and
  over-ceiling stop.

## Change Set
- `fix-review-preflight-investigation-authorization`

## Verify
- `python3 scripts/smoke-review-preflight.py`: PASS.
- `python3 scripts/smoke-contract-schemas.py`: PASS, 20 schemas.
- `ruff check scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py scripts/smoke-contract-schemas.py`: PASS.
- `python3 -m py_compile scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py scripts/smoke-contract-schemas.py`: PASS.
- `openspec validate fix-review-preflight-investigation-authorization --strict` and
  `openspec validate --all --strict`: PASS.
- `python3 scripts/public-surface-scan.py`: PASS, 960 files, 0 findings.
- `git diff --check`: PASS.
- `python3 scripts/smoke-windows-wiring-git-safety.py`: PASS, 6/6.
- `python3 scripts/run-release-baseline.py`: PASS, 34/34 steps.

## Archive
- `openspec/changes/archive/2026-08-17-fix-review-preflight-investigation-authorization/`

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `schemas/changerail-review-preflight-result.schema.json`
- `openspec/changes/archive/2026-08-17-fix-review-preflight-investigation-authorization/`

## Result
Implementation and verification are complete; the exact dirty payload awaits
one fresh independent ordinary `high` review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `fix-review-preflight-investigation-authorization`

### Why
The deterministic preflight cannot distinguish production Go from Go tests and
does not consume the bounded, published investigation decision that justifies
the successor payload.

### Goal
Keep the default complexity stop conservative while allowing a published,
reciprocally bound authorization source to authorize exactly one successor
within a 500 production-LOC ceiling and declared protocol allowance.

### Scope
- Extend deterministic preflight parsing, validation and result schema.
- Add focused smoke cases and minimal contract/template/methodology wording.
- Do not add a CLI override, model launch behavior or runtime integration.

### Acceptance
- Authorization validation is structured, exact-path/id bound and fail-closed.
- The normal 300 ceiling and protocol stop remain when authorization is absent
  or invalid.
- Valid authorization routes the ordinary payload to its single `high` review.

### Depends On
- `accelerate-risk-tiered-review-feedback`

### Related
- `openspec/changes/fix-review-preflight-investigation-authorization/`

## Log
- 2026-08-17T00:00:00Z follow-up card created from deterministic preflight
  review evidence.
- 2026-08-17T00:05:00Z fast-forward completed one apply-ready change; strict
  OpenSpec validation passed and the card entered delivery.
- 2026-08-17T00:20:00Z implementation, focused adversarial smoke, strict
  OpenSpec, public scan and the 34-step release baseline passed; payload is
  ready for independent ordinary review.
- 2026-08-17T00:25:00Z delta requirements synchronized and change archived;
  card remains in `3.inprogress` pending one independent ordinary review.
- 2026-08-17T08:16:40Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
