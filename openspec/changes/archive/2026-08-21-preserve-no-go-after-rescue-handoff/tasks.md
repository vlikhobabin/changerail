## 1. Terminal classification

- [x] 1.1 Split schema/semantic verdict validation from positive freshness in
  the runner fallback.
- [x] 1.2 Preserve `BLOCKED/review_verdict_invalid` for stale `go` and invalid
  verdicts.

## 2. Regression coverage and contracts

- [x] 2.1 Make the review-budget smoke create a tracked rescue handoff after
  final `no-go` and assert terminal `NO-GO`.
- [x] 2.2 Document negative fallback semantics in the normative runner spec and
  contracts guide.

## 3. Verification

- [x] 3.1 Run focused delivery-runner smoke and strict OpenSpec validation.
- [x] 3.2 Run the complete release baseline, public-surface checks and diff
  check.
- [ ] 3.3 Obtain fresh independent ordinary/high review.
