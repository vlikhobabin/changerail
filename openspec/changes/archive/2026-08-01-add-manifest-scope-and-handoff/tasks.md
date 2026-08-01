## 1. Manifest Contract

- [x] 1.1 Extend `schemas/changerail-delivery-manifest.schema.json` with concise `verification_summary`, `review_summary` and `final_card_state` objects.
- [x] 1.2 Update `scripts/changerail_delivery_manifest.py` validation and helper behavior for handoff summary fields without storing raw logs.
- [x] 1.3 Add `scope-check` CLI support with working-tree, staged and combined targets.
- [x] 1.4 Implement NUL-safe operation comparison for add, modify, delete and rename entries, including explicit missing, extra and mismatched diagnostics.

## 2. Workflow Integration

- [x] 2.1 Update delivery/review/publish contracts to mention manifest scope reconciliation and handoff summaries at the appropriate gates.
- [x] 2.2 Update `docs/changerail-contracts.md` with the public `scope-check` and handoff summary contract.
- [x] 2.3 Ensure ignored runtime paths are excluded from committable scope comparisons.

## 3. Verification

- [x] 3.1 Extend manifest/schema smokes with positive add/modify/delete/rename scope reconciliation coverage.
- [x] 3.2 Add negative staged extra, missing and mismatched fixtures that fail if false green scope-check behavior returns.
- [x] 3.3 Add path fixture coverage for spaces, quotes, Unicode, literal arrow text and a Linux non-UTF-8 path when supported.
- [x] 3.4 Run `python3 scripts/smoke-delivery-manifest.py`.
- [x] 3.5 Run `python3 scripts/smoke-delivery-manifest-derive.py`.
- [x] 3.6 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.7 Run `./bin/openspec validate add-manifest-scope-and-handoff --strict`.
- [x] 3.8 Run `./bin/openspec validate --all --strict`.
- [x] 3.9 Run `git diff --check`.
- [x] 3.10 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.11 Run `python3 scripts/run-release-baseline.py`.
