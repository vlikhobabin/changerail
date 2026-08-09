## 1. CLI Entrypoints

- [x] 1.1 Add `scripts/changerail_maintenance.py` with `validate-catalog` and `render-index` subcommands.
- [x] 1.2 Add POSIX and native Windows `bin/changerail-maintenance` wrappers through the shared Python runtime.
- [x] 1.3 Support `--catalog`, `--policy`, `--index`, `--check` and `--write` path/mode controls with fail-closed path validation.

## 2. Deterministic Index

- [x] 2.1 Implement stable index rendering from validated catalog records.
- [x] 2.2 Make default/check mode read-only and `--write` mutate only the configured generated index path.
- [x] 2.3 Add the generated ChangeRail dogfood index.

## 3. Smoke Coverage And Docs

- [x] 3.1 Extend repository knowledge smoke tests for CLI validation, index check drift and write idempotence.
- [x] 3.2 Extend Windows entrypoint smoke coverage for `changerail-maintenance`.
- [x] 3.3 Document helper usage and generated index behavior in `docs/changerail-contracts.md`.

## 4. Verification

- [x] 4.1 Run `bin/changerail-maintenance validate-catalog`.
- [x] 4.2 Run `bin/changerail-maintenance render-index --check`.
- [x] 4.3 Run focused repository knowledge smoke.
- [x] 4.4 Run `python3 scripts/smoke-windows-entrypoints.py`.
- [x] 4.5 Run `./bin/openspec validate add-knowledge-catalog-cli-and-index --strict`.
- [x] 4.6 Run `./bin/openspec validate --all --strict`.
- [x] 4.7 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.8 Run `git diff --check`.
