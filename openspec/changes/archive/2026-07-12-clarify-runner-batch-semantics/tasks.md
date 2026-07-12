## 1. Runner Boundary

- [x] 1.1 Update runner help/docstring to say single board card path.
- [x] 1.2 Update docs that mention batch runner semantics.
- [x] 1.3 Update specs to preserve single-card status semantics.

## 2. Verification

- [x] 2.1 Run `python3 -m py_compile bin/changerail-delivery-runner`.
- [x] 2.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 2.3 Run `./bin/openspec validate "clarify-runner-batch-semantics" --strict`.
- [x] 2.4 Run `./bin/openspec validate --all --strict`.
- [x] 2.5 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile scripts/changerail_review_verdict.py scripts/smoke-review-verdict-validation.py bin/changerail-delivery-runner` passed.
- `python3 scripts/smoke-delivery-runner.py` passed.
- `bin/changerail-delivery-runner run --help` shows `single repository-relative board card path`.
- `./bin/openspec validate clarify-runner-batch-semantics --strict` passed.
- `./bin/openspec validate --all --strict` passed with 17 items.
- `git diff --check` passed.
