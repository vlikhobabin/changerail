## 1. Publish Exact Authorization Source

- [x] 1.1 Preserve exactly one inline `Investigation authorization` object on
  the source card with the six generic fields, exact investigation and future
  successor ids/canonical paths, ceiling `500` and protocol flag `true`.
- [x] 1.2 Confirm reciprocal documentation: the published investigation blocks
  authorization and future successor, authorization depends on the
  investigation and blocks that successor, and the future-successor contract
  requires dependency on the investigation plus the exact two-field inline
  source reference.
- [x] 1.3 Keep the future successor uncreated until this source is published in
  `4.done`; do not add or modify production code, tests, schemas, parsers,
  helpers, workflows, CLI surfaces or runtime state.

## 2. Synchronize Release-CI Contract

- [x] 2.1 Sync the `changerail-release-ci` delta requirement that publishes
  this exact authorization source before the future successor can be created.
- [x] 2.2 Preserve independent successor acceptance at no more than 499
  executable LOC relative to
  `45a2de98924c61bb9e944767013ea09918bba4b0`; treat authorization ceiling `500`
  only as the gate and constrain protocol allowance `true` to the
  decision-defined affected/full-release authority boundary.
- [x] 2.3 Confirm the scoped payload has zero production, test and runtime LOC
  and introduces no successor card/code or credential, mutation or live
  authority.

## 3. Verify And Archive

- [x] 3.1 Run
  `bin/openspec validate authorize-bounded-tiered-release-verification-loop --strict`,
  `bin/openspec validate changerail-release-ci --strict` after synchronization
  and `bin/openspec validate --all --strict`.
- [x] 3.2 Parse `.mcp.json` with `python3 -m json.tool` and
  `.codex/config.toml` with Python `tomllib`.
- [x] 3.3 Run current-only `python3 scripts/public-surface-scan.py` and
  `bin/changerail-source-classification --workspace . --json check`; do not run
  `--history`, any benchmark or `scripts/run-release-baseline.py`.
- [x] 3.4 Run `git diff --check` and an explicit whitespace check over every
  untracked artifact before archive.
- [x] 3.5 Derive and scope-check the ignored delivery manifest, then run
  normalized review preflight and confirm ordinary/high routing, zero added
  executable LOC and no executable authority/protocol addition.
- [x] 3.6 Archive the completed change only after all docs-only checks pass;
  leave the authorization card ready for fresh independent ordinary review and
  scoped publication.
