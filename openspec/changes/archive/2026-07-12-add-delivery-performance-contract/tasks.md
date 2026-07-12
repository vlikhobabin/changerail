## 1. Contract Schema

- [x] 1.1 Extend `schemas/changerail-delivery-run.schema.json` with optional `performance` summary fields.
- [x] 1.2 Extend `usage` schema with cached input, uncached input and reasoning token breakdown fields.
- [x] 1.3 Add or update schema smoke fixtures that validate records with and without optional performance fields.

## 2. Docs And Specs

- [x] 2.1 Update `docs/changerail-contracts.md` with mandatory vs best-effort timing and usage semantics.
- [x] 2.2 Sync delta specs into `openspec/specs/changerail-contracts/spec.md` and `openspec/specs/changerail-delivery-observability/spec.md`.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.2 Run `./bin/openspec validate add-delivery-performance-contract --strict`.
- [x] 3.3 Run `git diff --check`.
