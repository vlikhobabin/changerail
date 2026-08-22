# Preserve NO-GO after rescue handoff mutation

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Review
- Risk tier: `ordinary`
- Review effort: `high`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Keep a schema-valid final `no-go` terminal signal authoritative after the
delivery worker creates its required tracked rescue or replacement handoff.
Freshness remains mandatory for every `go` path.

## Acceptance
- A schema-valid unpublished `no-go` verdict yields terminal `NO-GO` even when
  a post-review tracked rescue card makes its fingerprint stale.
- A stale `go` verdict remains `BLOCKED/review_verdict_invalid`.
- Invalid verdicts remain fail-closed and no reviewed payload is published.
- Delivery-runner smoke and the complete release baseline pass.

## Change Set
- `preserve-no-go-after-rescue-handoff`

## Change 1: `preserve-no-go-after-rescue-handoff`

### Goal
Split negative terminal classification from positive publish freshness in the
single-card runner fallback and cover the rescue-card mutation regression.

### Depends On
- none

### Size Budget
- At most 300 added production LOC.

## Verify
- `python3 scripts/smoke-delivery-runner.py`
- `bin/openspec validate --all --strict`
- `bin/verify-release`
- `git diff --check`
- fresh independent ordinary/high review

## Archive
`openspec/changes/archive/2026-08-21-preserve-no-go-after-rescue-handoff/`

## Result
Runner fallback now preserves a schema-valid final `no-go` after tracked rescue
handoff mutation while retaining exact freshness checks for every `go` path.
Focused delivery-runner smoke, strict OpenSpec validation, whitespace/public
surface checks and the complete ChangeRail release baseline pass.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-21: reproduced `review_verdict_invalid` after a final no-go created a tracked rescue card.
- 2026-08-21: split negative schema validation from positive freshness, added regression coverage and archived the change.
- 2026-08-21: review cycle 1 returned NO-GO; bounded rescue removed the authoritative test bypass and reconciled the older fallback requirement.
- 2026-08-21: review cycle 2 returned NO-GO; final bounded rescue narrowed the remaining stale-verdict smoke contract to stale `go` and made exhausted-budget `no-go` deterministic.
- 2026-08-21T11:57:17Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
