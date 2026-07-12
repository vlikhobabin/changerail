## 1. Runner Outcome Fallback

- [x] 1.1 Add runner helpers to resolve current board location for the card and
  inspect canonical review verdict evidence without parsing free-text logs.
- [x] 1.2 Change fallback outcome selection so authoritative JSONL terminal
  events still win, fresh unpublished `no-go` verdicts produce `NO-GO`, invalid
  or stale unpublished verdicts produce `BLOCKED`, and no blocking evidence
  preserves existing exit-code fallback.

## 2. Regression Smoke

- [x] 2.1 Extend `scripts/smoke-delivery-runner.py` fake workspace/launcher
  support to create unpublished cards and canonical review verdict evidence.
- [x] 2.2 Add a regression case for child exit `0` plus repeated no-go
  safety-stop evidence where runner status, printed terminal outcome and wrapper
  exit are all non-delivered.
- [x] 2.3 Add a sequential supervisor smoke check proving a second card is not
  started after the first runner returns the fallback `NO-GO`.
- [x] 2.4 Preserve existing smoke coverage for structured no-go, awaiting-review,
  non-terminal tool error, ordered terminal events and preflight failure.

## 3. Contracts And Docs

- [x] 3.1 Update `docs/changerail-contracts.md`,
  `openspec/specs/changerail-delivery-runner/spec.md` and
  `openspec/specs/changerail-contracts/spec.md` with the fallback evidence
  contract.
- [x] 3.2 Update `skills/changerail-deliver/SKILL.md` to document the structured
  terminal event expectation on review-gated safety stops.

## 4. Verification And Handoff

- [x] 4.1 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 4.2 Run `openspec validate fix-runner-review-safety-stop-outcome --strict`
  and `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python3 scripts/public-surface-scan.py` because public docs,
  skills and runner code are changed.
- [x] 4.5 Record verification outcomes, sync specs, archive the change and update
  the delivery manifest/card for review.
