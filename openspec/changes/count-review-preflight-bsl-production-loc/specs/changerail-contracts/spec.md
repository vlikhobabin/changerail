## ADDED Requirements

### Requirement: Review preflight counts declared production BSL
The deterministic review preflight MUST count added `.bsl` lines toward
production complexity only when the path is classified as production BSL source
by the consumer source-classification contract. Existing non-production path
parts MUST continue to exclude BSL tests, fixtures, examples, schemas,
templates, docs and OpenSpec artifacts from production complexity.

#### Scenario: Production BSL crosses default ceiling
- **WHEN** a scoped payload adds more than 300 lines to `.bsl` files under a
  declared production BSL source root
- **THEN** preflight reports those lines in `added_production_loc`
- **AND** preflight returns `investigation-required` unless a valid bounded
  published investigation authorization applies

#### Scenario: Non-production BSL is excluded
- **WHEN** a scoped payload adds `.bsl` files under `test`, `tests`,
  `fixtures`, `examples` or another built-in non-production root
- **THEN** those lines do not contribute to `added_production_loc`
- **AND** source-kind breakdown explains that no production BSL contribution was
  counted for those paths

#### Scenario: Existing source suffixes are unchanged
- **WHEN** a scoped payload adds Python, Go, JavaScript or executable helper
  files covered by the built-in classifier
- **THEN** their production complexity behavior remains the same as before this
  change
