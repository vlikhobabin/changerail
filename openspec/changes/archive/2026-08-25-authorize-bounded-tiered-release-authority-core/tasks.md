## 1. Publish Exact Scope A Authorization Source

- [x] 1.1 Preserve exactly one inline `Investigation authorization` object on
  the source card with the six generic fields, exact rescue and future
  successor ids/canonical paths, ceiling `500` and protocol flag `true`.
- [x] 1.2 Confirm reciprocal documentation: the published rescue blocks the
  authorization and future successor, the authorization depends on the rescue
  and blocks that successor, and the future-successor contract requires both
  dependencies plus the exact two-field inline source reference.
- [x] 1.3 Keep the future successor absent until this source is published in
  `4.done`; do not add or modify production code, tests, schemas, parsers,
  helpers, workflows, CLI surfaces or runtime state.

## 2. Synchronize Exclusive Release-CI Ownership

- [x] 2.1 Sync the `changerail-release-ci` delta requirement publishing this
  exact authorization source before the future Scope A successor is created.
- [x] 2.2 Preserve exclusive Scope A ownership of admission, exact 35-ID
  registry/digest, affected/full authority, atomic generic capture,
  receipt/schema/preflight/publish gates, canonical CI runner and parsed
  YAML/Python-AST oracles.
- [x] 2.3 Exclude Scope B Windows scheduler/deduplication, verify-project,
  history scanner and review/delivery smoke internals; retain `<=499`
  production LOC against
  `25f756ebf2aa90c58e01eab3703b291dbdde257f` and zero executable LOC here.

## 3. Verify And Archive

- [x] 3.1 Run
  `bin/openspec validate authorize-bounded-tiered-release-authority-core --strict`,
  `bin/openspec validate changerail-release-ci --strict` after synchronization
  and `bin/openspec validate --all --strict`.
- [x] 3.2 Parse `.mcp.json` with `python3 -m json.tool` and
  `.codex/config.toml` with Python `tomllib`.
- [x] 3.3 Run current-only `python3 scripts/public-surface-scan.py` and
  `bin/changerail-source-classification --workspace . --json check`; do not
  run `--history`, a benchmark or `scripts/run-release-baseline.py`.
- [x] 3.4 Run `git diff --check` and an explicit whitespace check over every
  untracked artifact.
- [x] 3.5 Derive and scope-check the ignored delivery manifest, then run
  normalized review preflight and confirm ordinary/high routing, zero added
  production LOC and no authority outside the exact docs-only authorization.
- [x] 3.6 Archive the completed change only after all docs-only checks pass;
  leave the source ready for fresh independent ordinary review and scoped
  publication.
