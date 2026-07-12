## 1. Helper

- [x] 1.1 Add `derive` command to `scripts/changerail_delivery_manifest.py`.
- [x] 1.2 Parse board card metadata and ordered changes.
- [x] 1.3 Classify active/archived/planned changes and archive paths.
- [x] 1.4 Derive committable paths from `git status --porcelain` without
  including ignored runtime state.
- [x] 1.5 Preserve existing `validate` and `staging-plan` behavior.

## 2. Smoke Coverage

- [x] 2.1 Add focused smoke coverage for manifest derivation and staging plan.
- [x] 2.2 Include add/modify/delete/rename or documented operation coverage.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile scripts/changerail_delivery_manifest.py`.
- [x] 3.2 Run manifest helper smoke.
- [x] 3.3 Run `./bin/openspec validate "derive-delivery-manifest" --strict`.
- [x] 3.4 Run `./bin/openspec validate --all --strict`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile scripts/changerail_delivery_manifest.py` passed.
- `python3 scripts/smoke-delivery-manifest.py` passed.
- `python3 scripts/smoke-delivery-manifest-derive.py` passed with
  `SMOKE_DELIVERY_MANIFEST_DERIVE_OK`.
- `./bin/openspec validate derive-delivery-manifest --strict` passed.
- `./bin/openspec validate --all --strict` passed with 18 items before archive.
- `git diff --check` passed.
