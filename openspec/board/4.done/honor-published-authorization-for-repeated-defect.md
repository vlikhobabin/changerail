# Учитывать published authorization для repeated defect preflight

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
- Safety stop в consumer delivery: exact published investigation authorization
  валидна, но deterministic preflight всё равно безусловно останавливает
  successor с `Repeated defect class: yes`.

## Summary
Применить уже проверенную exact published authorization ко всему bounded
complexity decision: валидная authorization снимает repeated-defect stop только
для связанного successor, а отсутствующая или invalid authorization остаётся
fail-closed.

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
- Exact successor с `Repeated defect class: yes` и valid published authorization
  проходит complexity guard и направляется в объявленный semantic review.
- Тот же repeated signal без authorization или с invalid authorization возвращает
  `investigation-required` до model launch.
- LOC ceiling и protocol allowance продолжают применяться независимо и
  fail-closed; authorization не становится reusable waiver.
- Focused smoke содержит regression case для valid authority и negative case
  для отсутствующей authority, а полный release baseline остаётся зелёным.

## Change Set
- `honor-published-authorization-for-repeated-defect`

## Verify
- `python3 scripts/smoke-review-preflight.py`: RED reproduced the unconditional
  repeated stop, then GREEN passed with authorized and unauthorized controls.
- `ruff check scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`:
  PASS.
- `python3 -m py_compile scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`:
  PASS.
- `bin/openspec validate honor-published-authorization-for-repeated-defect --strict`
  and `bin/openspec validate --all --strict`: PASS before archive.
- `python3 scripts/public-surface-scan.py`: PASS, 1263 files, 0 findings.
- `git diff --check`: PASS, including intent-to-add planning paths.
- `python3 scripts/run-release-baseline.py`: direct pre-archive run PASS,
  36/36 steps; final post-archive retained rerun is the publish floor.

## Archive
- `openspec/changes/archive/2026-08-22-honor-published-authorization-for-repeated-defect/`

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `openspec/changes/honor-published-authorization-for-repeated-defect/`

## Result
Implementation, focused regression coverage, contract sync and archive are
complete. The reviewed payload awaits one fresh independent ordinary review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `honor-published-authorization-for-repeated-defect`

### Why
Authorization validation already proves an exact clean `4.done` source,
investigation and successor graph, but the repeated-defect branch ignores that
validated state.

### Goal
Use the same exact authorization state for the repeated-defect complexity
signal while preserving all absent/invalid, ceiling and protocol stops.

### Scope
- Change only deterministic preflight complexity routing and its focused smoke.
- Clarify the existing contract and methodology requirements.
- Do not add fields, CLI overrides, reusable waivers or model-launch behavior.

### Acceptance
- Valid exact authorization permits `Repeated defect class: yes` only for its
  bound successor.
- Missing or invalid authorization keeps the repeated-defect stop.
- Existing LOC/protocol authorization checks remain unchanged.

### Depends On
- `fix-review-preflight-investigation-authorization`

### Related
- `openspec/changes/honor-published-authorization-for-repeated-defect/`

## Log
- 2026-08-22T00:00:00Z safety stop reproduced; one bounded apply-ready fix
  created from the existing published-authorization contract.
- 2026-08-22T07:18:14Z focused RED/GREEN, lint, compile, strict OpenSpec,
  public scan, whitespace and 36-step release baseline passed; specs were
  synchronized and the change archived for independent review.
- 2026-08-22T08:14:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
