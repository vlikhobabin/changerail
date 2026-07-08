## 1. Contract Schemas

- [x] 1.1 Add `schemas/opsx-review-verdict.schema.json` with canonical OPSX id.
- [x] 1.2 Add `schemas/opsx-delivery-manifest.schema.json` with canonical OPSX id.
- [x] 1.3 Add `schemas/opsx-evidence-index.schema.json` with canonical OPSX id.

## 2. Helper

- [x] 2.1 Add `scripts/opsx_review_verdict.py`.
- [x] 2.2 Add executable `bin/opsx-review-verdict` wrapper.
- [x] 2.3 Document helper validate and fingerprint usage.

## 3. Verification

- [x] 3.1 Run `openspec validate "add-opsx-contract-schemas-and-helper" --strict`.
- [x] 3.2 Run `python3 -m json.tool` for each schema file.
- [x] 3.3 Run `python3 scripts/opsx_review_verdict.py fingerprint --workspace .`.
- [x] 3.4 Run helper validation against a generated canonical sample verdict.
- [x] 3.5 Run public-surface scan for private paths and `git diff --check`.

## Verification Notes

- `openspec validate add-opsx-contract-schemas-and-helper --strict` passed.
- `python3 -m json.tool` passed for `.mcp.json` and all three `schemas/opsx-*.schema.json` files.
- `python3 scripts/opsx_review_verdict.py fingerprint --workspace .` emitted a `sha256:<hex>` fingerprint.
- Generated runtime verdict sample with `opsx.review-verdict.v1` validated with
  `--check-fresh`.
- Targeted public-path scan returned no private path matches.
- `git diff --check` passed.
