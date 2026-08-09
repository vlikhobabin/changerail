## 1. Feedback CLI And Normalization

- [x] 1.1 Add `feedback` parser options to `scripts/changerail_maintenance.py` and preserve POSIX/Windows wrapper behavior.
- [x] 1.2 Add review-history validation and normalization helpers for `changerail.review-cycle-history.v1` inputs.
- [x] 1.3 Add blocked delivery-run validation and normalization helpers for `changerail.delivery-run.v1` terminal records.
- [x] 1.4 Add external detector-result merge support with the existing safe-path validation semantics.
- [x] 1.5 Ensure mixed malformed, unsafe or incomplete inputs produce detector errors and `error` status instead of a silent pass.

## 2. Fixtures And Tests

- [x] 2.1 Add public-safe review-history fixtures for positive, multiple-path and unsafe-path cases.
- [x] 2.2 Add public-safe delivery-run fixtures for structured blocked, non-blocked and prose-only unsupported cases.
- [x] 2.3 Add external producer fixtures for valid and unsafe detector-result inputs.
- [x] 2.4 Extend `scripts/smoke-repository-knowledge.py` to cover feedback output shape, status, identity metadata and read-only behavior.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate connect-maintenance-feedback-adapters --strict`.
- [x] 3.2 Run `python3 scripts/smoke-repository-knowledge.py`.
- [x] 3.3 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Run `python3 scripts/public-surface-scan.py`.
