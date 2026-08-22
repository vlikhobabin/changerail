## 1. Record bounded decisions

- [x] 1.1 Record exact ids and future `3.inprogress` paths for all six blocked
  successors.
- [x] 1.2 Record per-successor single-source/shared-helper boundaries,
  production budgets and required verification floors.
- [x] 1.3 State ceiling 500, protocol allowance and fail-closed split behavior
  separately for every successor.

## 2. Resolve repeated-defect routing

- [x] 2.1 Bind target substitution, external resume, verification coverage and
  source-profile symptoms to one investigated hypothesis each.
- [x] 2.2 Update successor review metadata/dependencies so post-investigation
  implementation is not treated as an unbounded repeated rescue.
- [x] 2.3 Preserve logs stating that another same blocker requires a new linked
  investigation/split and receives no extra rescue budget.

## 3. Publish investigation contract

- [x] 3.1 Sync the bounded decision into `changerail-contracts` and archive the
  decision-only OpenSpec change without production code.
- [x] 3.2 Run strict OpenSpec validation, public-surface scan and whitespace
  checks.
- [x] 3.3 Prepare exact source data for six separate authorization cards; do not
  create a reusable/global waiver.
