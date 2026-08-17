# Ускорить risk-tiered review feedback

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
- Анализ затянувшегося autonomous delivery: process-only defects многократно
  запускали дорогой payload review, а planning, implementation и live-admission
  циклы расходовали общий неявный budget.

## Summary
Добавить единый deterministic review preflight и небольшой risk-tier contract,
чтобы manifest/scope/board/freshness defects исправлялись до LLM review,
обычные изменения проверялись с `high`, а `xhigh` использовался только для
критичных authority, credential, mutation, live-admission и final-certification
границ. Ограничить patch staircase typed complexity stop-ом.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`

## Acceptance
- Existing review-verdict helper exposes a deterministic preflight that validates
  and safely normalizes manifest metadata/operation mismatches without widening
  scope, checks board/archive/scope, and runs strict OpenSpec, diff and public
  checks when available.
- Preflight emits a schema-valid machine result and blocks before LLM launch on
  process defects; a deterministic/process card needs no LLM when machine gates
  pass, ordinary review routes to `high`, and critical review routes to `xhigh`.
- Planning, delivery-fix, implementation-review and live-admission counters are
  separate; planning or preflight failures do not consume implementation rescue
  budget.
- Every publish has exactly one risk-appropriate payload review. An extra
  clean-HEAD LLM audit is allowed once only at a declared milestone, while
  unchanged hash-bound full-suite evidence may be reused for a focused re-review
  and is rerun before live admission or final publish.
- More than 300 added production LOC, a new authority/wire protocol, or a
  repeated defect class produces a typed investigation/simplification stop
  instead of another implementation patch.
- Canonical skills, shared methodology, consumer runbook and both card templates
  describe the accelerated flow; focused deterministic smoke and full release
  baseline pass.

## Change Set
- `accelerate-risk-tiered-review-feedback`

## Verify
- `python3 scripts/smoke-review-preflight.py`: PASS.
- `python3 scripts/smoke-contract-schemas.py`: PASS, 20 schemas.
- `ruff check scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`:
  PASS after review-cycle-1 rescue R1.
- `python3 -m py_compile scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`:
  PASS after review-cycle-1 rescue R1.
- `python3 scripts/smoke-review-preflight.py`: PASS after adding extensionless
  `bin/` complexity/deterministic regressions and a `docs/` exclusion regression.
- `python3 scripts/run-release-baseline.py`: PASS, 34/34 steps.
- Full baseline includes strict OpenSpec, Python syntax/lint, public current and
  history scans, review/manifest/delivery smoke, consumer bootstrap and drift.

## Archive
- `openspec/changes/archive/2026-08-17-accelerate-risk-tiered-review-feedback/`

## Related
- `openspec/changes/accelerate-risk-tiered-review-feedback/`
- `scripts/changerail_delivery_manifest.py`
- `scripts/changerail_review_verdict.py`
- `skills/changerail-review/SKILL.md`
- `skills/changerail-deliver/SKILL.md`
- `docs/how-it-works.md`

## Result
Implementation and bounded review-cycle-1 rescue R1 are complete. The exact
dirty payload is reserved for focused independent re-review; no self-review,
commit or publish was performed.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `accelerate-risk-tiered-review-feedback`

### Why
LLM reviewers currently receive deterministic process defects and repeat broad
reviews after corrections that did not change the payload risk. The shared
five-cycle rescue language also encourages patch staircases instead of early
simplification.

### Goal
Put cheap deterministic checks before payload review, route semantic review by
risk, separate phase counters and stop runaway rescue complexity without adding
a model-launch orchestration layer.

### Scope
- Extend the existing review-verdict/manifest helpers with one preflight command
  and one machine-result schema.
- Extend review-cycle history with optional phase counters.
- Add focused smoke coverage.
- Update canonical methodology, lifecycle skills, runbook, templates and main
  OpenSpec capabilities.

### Acceptance
- Preflight never widens manifest scope and never invokes an LLM.
- Process defects return machine-readable blockers before payload review.
- Review route and reasoning effort follow declared risk.
- Complexity guard returns a typed investigation stop at the declared limits.
- Review count/evidence reuse/milestone rules are unambiguous in shared sources.

### Depends On
- none

### Related
- `openspec/changes/accelerate-risk-tiered-review-feedback/`

## Log
- 2026-08-17T00:00:00Z emergency process-acceleration card created from the
  autonomous-delivery review audit.
- 2026-08-17T00:05:00Z fast-forward planning completed one apply-ready change;
  strict OpenSpec validation passed and the card moved to `3.inprogress`.
- 2026-08-17T05:31:41Z implementation, spec sync and the 34-step pre-archive
  release baseline completed; payload retained dirty for independent review.
- 2026-08-17T05:52:00Z independent review cycle 1 returned NO-GO with blocker
  R1: extensionless executable production entrypoints under `bin/` were not
  classified as production by the LOC and deterministic-risk guards.
- 2026-08-17T05:53:57Z bounded same-card rescue R1 classified extensionless
  executable root `bin/` entrypoints, retained nonproduction exclusions and
  added focused regressions; payload retained dirty for review cycle 2.
- 2026-08-17T06:16:46Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
