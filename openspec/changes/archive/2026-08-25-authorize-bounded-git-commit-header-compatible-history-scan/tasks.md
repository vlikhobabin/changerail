## 1. Publish Exact Authorization Source

- [x] 1.1 Preserve exactly one inline `Investigation authorization` object on
  the source card with the six generic fields, exact rescue investigation and
  future replacement ids/canonical paths, ceiling `301` and protocol flag
  `false`.
- [x] 1.2 Confirm reciprocal documentation: the published rescue investigation
  blocks authorization and future replacement, authorization depends on the
  investigation and blocks that replacement, and the future-replacement
  contract requires dependency on the investigation plus the exact two-field
  inline source reference. Repair only an exact successor link if current
  relation docs have drifted.
- [x] 1.3 Keep the future replacement uncreated until this source is published
  in `4.done`; do not add or modify production code, tests, schemas, parsers,
  helpers, workflows, CLI surfaces or runtime state.

## 2. Synchronize Release-CI Contract

- [x] 2.1 Sync the `changerail-release-ci` delta requirement that publishes
  this exact authorization source before the future replacement can be
  created.
- [x] 2.2 Preserve independent successor acceptance at no more than 300 added
  production LOC relative to
  `ccccb62562e1646b595119edd3326763860f14a7`; treat authorization ceiling
  `301` only as the minimal schema-valid gate and retain protocol allowance
  `false`.
- [x] 2.3 Confirm the scoped payload has zero production, test and runtime LOC
  and introduces no successor card/code, new authority or wire protocol.

## 3. Verify And Archive

- [x] 3.1 Run
  `bin/openspec validate authorize-bounded-git-commit-header-compatible-history-scan --strict`,
  `bin/openspec validate changerail-release-ci --strict` after synchronization
  and `bin/openspec validate --all --strict`.
- [x] 3.2 Parse `.mcp.json` with `python3 -m json.tool` and
  `.codex/config.toml` with Python `tomllib`.
- [x] 3.3 Run the current-only `python3 scripts/public-surface-scan.py` and
  `bin/changerail-source-classification --workspace . --json check`; do not
  run `--history`, any benchmark or `scripts/run-release-baseline.py`.
- [x] 3.4 Run `git diff --check` and an explicit whitespace check over every
  untracked artifact before archive.
- [x] 3.5 Derive and scope-check the ignored delivery manifest, then run
  normalized review preflight and confirm ordinary/high routing, zero added
  production LOC and no authority/protocol addition; lifecycle-only blocking
  before archive/publication is expected.
- [x] 3.6 Archive the completed change only after all docs-only checks pass;
  leave the authorization card ready for independent ordinary review and
  scoped publication.
