## 1. Helper Implementation

- [x] 1.1 Add deterministic untracked non-ignored content hashing to `scripts/opsx_review_verdict.py`.
- [x] 1.2 Preserve `sha256:<64 hex>` fingerprint output and existing `validate --check-fresh` behavior.

## 2. Smoke Coverage

- [x] 2.1 Add a smoke script under `scripts/` that proves untracked content changes alter the fingerprint.
- [x] 2.2 Extend the smoke script to prove ignored runtime content does not alter the fingerprint.

## 3. Documentation And Contracts

- [x] 3.1 Update `docs/opsx-contracts.md` with the strengthened freshness source set.
- [x] 3.2 Update `skills/opsx-review/references/opsx-review-verdict.md` while preserving reviewer defense-in-depth guidance.

## 4. Verification

- [x] 4.1 Run `openspec validate "harden-verdict-fingerprint" --strict`.
- [x] 4.2 Run the new smoke script.
- [x] 4.3 Run `python3 -m py_compile scripts/opsx_review_verdict.py` and the new smoke script.
- [x] 4.4 Run `openspec validate --all --strict`.
- [x] 4.5 Run public-surface scan and `git diff --check`.

## Verification Notes

- RED: `python3 scripts/smoke-review-fingerprint.py` failed before helper
  changes with `AssertionError: untracked non-ignored content change did not
  alter fingerprint`.
- passed: `openspec validate harden-verdict-fingerprint --strict`
- passed: `python3 scripts/smoke-review-fingerprint.py`
- passed: `python3 -m py_compile scripts/opsx_review_verdict.py
  scripts/smoke-review-fingerprint.py`
- passed: `python3 scripts/opsx_review_verdict.py fingerprint --workspace .`
  emitted `sha256:00f5acad9386d841aae4dab4bb0af40e208dccd227121ed2998abd823a89cfd2`.
- passed: `openspec validate --all --strict` (12 passed, 0 failed).
- passed: `git diff --check`
- passed: targeted public-surface scan; matches were existing generic
  public-safety wording and Python `secrets` module imports, with no unexpected
  private names, credentials or local paths found.
