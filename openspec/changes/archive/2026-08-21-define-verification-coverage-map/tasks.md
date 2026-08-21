## 1. Map contract

- [x] 1.1 Add RED schema fixtures for the five-field entry model, duplicate ids,
  unsafe globs, missing selectors, oracle/evidence mismatches and undeclared
  policy fields.
- [x] 1.2 Add `changerail.verification-coverage.v1` schema with normalized
  path/operation selectors and opaque namespaced surface kinds.
- [x] 1.3 Add canonical map fingerprinting and fail-closed YAML loading without
  executing commands or loading network data.

## 2. Plan and ledger contracts

- [x] 2.1 Add schemas for tracked per-change coverage references and ignored
  runtime ledgers with map/card/manifest/review fingerprints.
- [x] 2.2 Prove plan/ledger reference ids and acceptance hashes without copying
  invariant, oracle, criterion text, final verdict or raw evidence.
- [x] 2.3 Add schemas and docs to contract inventory and
  `scripts/smoke-contract-schemas.py`.

## 3. Project configuration and examples

- [x] 3.1 Add optional `verification.coverage_map` to project config template
  and generated guidance without enabling placeholder gates by default.
- [x] 3.2 Add one synthetic generic Python map/fixture with project-owned
  test/lint/type/runtime policy only where explicitly declared.
- [x] 3.3 Document namespaced domain extension boundary and demonstrate
  specialized surface ids as data without embedding domain tools/rules in core.

## 4. Verification

- [x] 4.1 Run `python3 scripts/smoke-contract-schemas.py` and observe valid,
  invalid, plan and ledger fixtures pass.
- [x] 4.2 Run `python3 scripts/smoke-bootstrap-project.py` and
  `python3 scripts/smoke-verify-project.py`; observe no-map consumers retain
  existing behavior and configured fixtures validate.
- [x] 4.3 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`; record concise outcomes and keep
  runtime artifacts ignored.
