## 1. Policy And Contract

- [x] 1.1 Extend maintenance policy adapter configuration with id, argv, timeout and options fields.
- [x] 1.2 Extend scan report/result validation coverage for adapter findings and detector-error outcomes.
- [x] 1.3 Document adapter protocol and failure semantics in `docs/changerail-contracts.md`.

## 2. Adapter Execution

- [x] 2.1 Implement shell-free adapter execution from repository cwd with timeout handling.
- [x] 2.2 Map schema-valid adapter output into scan detector findings.
- [x] 2.3 Convert adapter non-zero exit, timeout, invalid JSON and unsafe paths into detector-error results.
- [x] 2.4 Preserve no-mutation scan behavior when adapter detector is enabled.

## 3. Fixtures And Verification

- [x] 3.1 Add generic adapter fixtures for valid output, timeout, invalid output and unsafe paths.
- [x] 3.2 Run focused repository knowledge smoke with adapter fixtures.
- [x] 3.3 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.4 Run `bin/changerail-maintenance scan --json`.
- [x] 3.5 Run `./bin/openspec validate add-maintenance-detector-adapter-protocol --strict`.
- [x] 3.6 Run `./bin/openspec validate --all --strict`.
- [x] 3.7 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.8 Run `git diff --check`.
