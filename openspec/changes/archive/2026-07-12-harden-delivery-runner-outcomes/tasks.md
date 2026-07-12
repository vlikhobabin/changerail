## 1. Runner Outcome Parsing

- [x] 1.1 Заменить recursive arbitrary string outcome scanning на parsing documented structured event/terminal field.
- [x] 1.2 Сохранить ordered stdout handling, чтобы последний authoritative terminal event определял structured outcome.
- [x] 1.3 Сохранить process exit fallback behavior для successful exit, non-zero exit и preflight failure.

## 2. Schema Coverage

- [x] 2.1 Расширить `bin/verify-project` schema coverage до review verdict, review history, delivery manifest, delivery run и evidence index.
- [x] 2.2 Обновить docs/spec references для complete public schema coverage.

## 3. Regression Coverage

- [x] 3.1 Расширить `scripts/smoke-delivery-runner.py` для non-terminal error strings, ordered conflicting events, non-zero exit without outcome, authoritative no-go и awaiting-review.
- [x] 3.2 Расширить `scripts/smoke-verify-project.py`, чтобы assert все пять schema checks.

## 4. Verification

- [x] 4.1 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 4.2 Run `python3 scripts/smoke-verify-project.py`.
- [x] 4.3 Run `openspec validate harden-delivery-runner-outcomes --strict`.
- [x] 4.4 Run `git diff --check`.
