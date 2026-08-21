## 1. Helper surface

- [ ] 1.1 Add `bin/changerail-source-classification` and Windows wrapper using
  supported runtime Python plus help/JSON contract smoke coverage.
- [ ] 1.2 Implement profile source loading, schema/checksum validation and
  bounded source reporting for built-in and explicit local inputs.

## 2. Read-only detection

- [ ] 2.1 Add RED fixtures proving default detection reads tracked `HEAD`, not
  dirty worktree markers, and rejects invalid/non-tree snapshots.
- [ ] 2.2 Implement path-only weighted signal matching, required signals,
  deterministic confidence bands, ambiguities and recommended actions.
- [ ] 2.3 Add synthetic generic, mixed-stack, unknown-suffix and structural XML
  candidate fixtures without real domain/customer source.
- [ ] 2.4 Prove detect performs no writes and unaccepted candidates do not change
  preflight `added_production_loc`, risk or admission.

## 3. Preview and materialization

- [ ] 3.1 Implement explicit ordered profile selection and default no-write
  semantic preview with id/version/checksum/source report.
- [ ] 3.2 Implement `--write` revalidation and atomic creation of canonical
  schema-valid classification with provenance.
- [ ] 3.3 Add idempotent matching-file no-op and fail-closed semantic diff for
  any differing existing file; do not add force overwrite.
- [ ] 3.4 Prove review preflight changes only after the project classification
  exists and passes its existing schema check.

## 4. Wiring and verification

- [ ] 4.1 Add helper inventory/bootstrap wiring and operator docs for explicit
  profile sources, preview and tracked policy ownership.
- [ ] 4.2 Run focused source-profile helper smokes plus
  `python3 scripts/smoke-review-preflight.py`; observe detection,
  materialization, idempotence, conflict and risk-boundary cases pass.
- [ ] 4.3 Run `python3 scripts/smoke-bootstrap-project.py`,
  `python3 scripts/smoke-verify-project.py` and Windows wrapper checks; observe
  generated consumers discover the helper consistently.
- [ ] 4.4 Run `bin/openspec validate --all --strict`, `git diff --check`,
  `python3 scripts/public-surface-scan.py` and the risk-appropriate release
  baseline; retain runtime reports outside Git.
