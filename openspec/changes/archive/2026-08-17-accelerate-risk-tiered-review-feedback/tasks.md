## 1. Deterministic Preflight

- [x] 1.1 Add a schema for machine-readable review preflight results.
- [x] 1.2 Extend the existing review-verdict helper with preflight routing that
  reuses manifest validation, safe normalization, scope comparison and verdict
  fingerprinting.
- [x] 1.3 Run available strict OpenSpec, diff and public checks before LLM review.
- [x] 1.4 Add risk routing and the typed rescue complexity guard.

## 2. Runtime Contracts

- [x] 2.1 Add optional per-phase counters to review-cycle history without
  invalidating legacy records.
- [x] 2.2 Extend contract and focused smoke coverage for schema, normalization,
  scope blocker, risk routing and complexity-stop behavior.
- [x] 2.3 Add the public schema to consumer verification and the focused smoke to
  release baseline inventory.

## 3. Methodology And Consumer Surface

- [x] 3.1 Update shared methodology and workflow docs for one payload review,
  one declared milestone audit, hash-bound evidence reuse and final full-suite
  rerun.
- [x] 3.2 Update review, deliver, do and publish skills with preflight, risk-tier,
  counter and complexity-stop rules.
- [x] 3.3 Update the consumer runbook and both card templates with review fields.

## 4. Verification And Archive

- [x] 4.1 Run focused preflight and contract schema smoke tests.
- [x] 4.2 Run strict OpenSpec validation, Python compile/lint, public-surface scan,
  diff check and the full release baseline.
- [x] 4.3 Sync delta requirements to main specs and archive this change.
- [x] 4.4 Leave the card in `3.inprogress` with one review-ready dirty payload;
  do not self-review, commit or push.
