## 1. Scanner

- [x] 1.1 Add `scripts/public-surface-scan.py`.
- [x] 1.2 Support explicit file/directory path arguments.
- [x] 1.3 Support default public-surface roots.
- [x] 1.4 Add allowlists for generic examples and historical `opsx` references.

## 2. Smoke Coverage

- [x] 2.1 Add self-test or smoke fixture for allowed generic paths.
- [x] 2.2 Add negative fixture for disallowed `/opt/<private>` path.
- [x] 2.3 Add regression coverage proving default roots scan archived OpenSpec
  changes.

## 3. Verification

- [x] 3.1 Run scanner self-test.
- [x] 3.2 Run scanner against touched public files.
- [x] 3.3 Run `./bin/openspec validate "add-public-surface-scan-helper" --strict`.
- [x] 3.4 Run `./bin/openspec validate --all --strict`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 scripts/public-surface-scan.py --self-test` passed with
  `PUBLIC_SURFACE_SCAN_SELF_TEST_OK`.
- `python3 scripts/public-surface-scan.py` passed against default public
  surfaces including archived OpenSpec artifacts.
- `python3 scripts/public-surface-scan.py openspec/changes/archive` passed
  against archived OpenSpec artifacts.
- `./bin/openspec validate add-public-surface-scan-helper --strict` passed.
- `./bin/openspec validate --all --strict` passed with 18 items before archive.
- `git diff --check` passed.
