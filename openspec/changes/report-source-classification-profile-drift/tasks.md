## 1. Check contract

- [ ] 1.1 Add `changerail.source-classification-check.v1` schema and RED fixtures
  for matching baseline, declared override, immutable checksum conflict,
  undeclared drift and unavailable local profile.
- [ ] 1.2 Implement read-only `check` loading final classification, confirmed
  built-in/explicit local baselines and exact declared override paths.
- [ ] 1.3 Emit bounded effective-rule/provenance/covered/excluded/uncovered
  summaries without source contents or machine-absolute paths.

## 2. Drift and uncovered diagnostics

- [ ] 2.1 Classify invalid policy, measurement conflict, checksum conflict and
  confirmed undeclared profile divergence as blocking.
- [ ] 2.2 Reuse tracked HEAD/snapshot signals for advisory unaccepted candidates
  with bounded confidence/counts/capped normalized examples.
- [ ] 2.3 Add synthetic mixed-stack, unknown domain suffix, structural XML,
  selected-profile omission and project-override fixtures.
- [ ] 2.4 Prove advisory candidates never alter final classification,
  `added_production_loc` or review route.

## 3. Verification integration and guidance

- [ ] 3.1 Integrate schema-valid blocking check results into project verification
  and review preflight after final classification calculation.
- [ ] 3.2 Keep low/high-confidence unaccepted candidates as diagnostics and make
  confirmed selected-profile undercoverage fail closed.
- [ ] 3.3 Update templates/docs for `detect -> review -> materialize -> check`,
  explicit local profile supply and separate reviewed migration without force.

## 4. Verification

- [ ] 4.1 Run focused source-profile helper smokes,
  `python3 scripts/smoke-review-preflight.py` and
  `python3 scripts/smoke-verify-project.py`; observe blocking/advisory/risk
  invariants pass.
- [ ] 4.2 Run `python3 scripts/smoke-contract-schemas.py` and observe check-report
  and legacy classification fixtures pass.
- [ ] 4.3 Run `python3 scripts/smoke-bootstrap-project.py` and Windows wrapper
  checks; observe generated lifecycle guidance/surfaces remain consistent.
- [ ] 4.4 Run `bin/openspec validate --all --strict`, `git diff --check`,
  `python3 scripts/public-surface-scan.py` and risk-appropriate release baseline;
  keep raw reports ignored.
