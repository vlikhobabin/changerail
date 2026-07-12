## 1. Review Orchestration

- [x] 1.1 Update `changerail-deliver` with a standard fresh reviewer prompt or
  invocation contract.
- [x] 1.2 Document validation of `reviewer.independence` and `--check-fresh`
  before publish.

## 2. Publish Finalization

- [x] 2.1 Update `changerail-pub` with deterministic card finalization steps.
- [x] 2.2 Add helper support for final card move/status/log/result metadata when
  practical.
- [x] 2.3 Add helper support for ignored manifest publish metadata updates.

## 3. Verification

- [x] 3.1 Run focused helper smoke for finalization/publish metadata if helper
  code is added.
- [x] 3.2 Run `./bin/openspec validate "automate-review-and-publish-finalization" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `python3 scripts/smoke-delivery-manifest-derive.py` passed and covers
  `publish-update` plus `finalize-card`.
- `./bin/openspec validate automate-review-and-publish-finalization --strict` passed.
- `./bin/openspec validate --all --strict` passed with 18 items before archive.
- `git diff --check` passed.
