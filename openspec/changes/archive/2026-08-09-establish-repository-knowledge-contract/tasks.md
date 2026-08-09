## 1. Schemas And Loader

- [x] 1.1 Add repository knowledge and maintenance policy JSON Schemas with canonical schema ids.
- [x] 1.2 Implement shared YAML/schema loading and structured diagnostics in `scripts/changerail_repository_knowledge.py`.
- [x] 1.3 Enforce repository-relative path normalization, active path existence and fail-closed absolute/traversal rejection.

## 2. Fixtures And Dogfood

- [x] 2.1 Add public-safe valid and invalid catalog/policy fixtures, including unknown-field and traversal cases.
- [x] 2.2 Add a minimal ChangeRail dogfood catalog/policy skeleton at the default tracked paths.

## 3. Docs And Specs

- [x] 3.1 Document schema ids, default paths, record fields, enum values and null/empty semantics in `docs/changerail-contracts.md`.
- [x] 3.2 Add the new repository knowledge OpenSpec capability and contract schema requirements.

## 4. Verification

- [x] 4.1 Run focused repository knowledge fixture smoke.
- [x] 4.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.3 Run `./bin/openspec validate establish-repository-knowledge-contract --strict`.
- [x] 4.4 Run `./bin/openspec validate --all --strict`.
- [x] 4.5 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.6 Run `git diff --check`.
