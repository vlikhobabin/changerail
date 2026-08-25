## 1. Publish Exact Authorization Source

- [x] 1.1 Preserve exactly one inline `Investigation authorization` object on
  the source card with the six generic fields, exact decision/future-successor
  ids and canonical paths, ceiling `500` and protocol flag `true`.
- [x] 1.2 Confirm reciprocal documentation: the published decision blocks the
  authorization and future successor; authorization depends on the decision and
  blocks that successor; future successor requires decision dependency plus the
  exact two-field source reference.
- [x] 1.3 Keep future successor, executable implementation, production code,
  tests and runtime state absent; record zero production/test/runtime/executable
  LOC and no new authority or wire protocol in this payload.

## 2. Synchronize Release-CI Contract

- [x] 2.1 Sync the `changerail-release-ci` delta that publishes this exact I
  authorization source before the future successor can be created.
- [x] 2.2 Preserve independent future acceptance at `<=499` executable LOC
  relative to its exact published authorization HEAD; constrain allowance `true`
  to I ownership only: isolated case schemas, jobs/order, hard output/timeout
  bounds, process containment, cleanup and parsed-CI proof.
- [x] 2.3 Confirm the docs-only payload adds no credential, mutation, live or
  terminal authority and does not add registry selection, history parsing or
  receipt ownership.

## 3. Verify And Archive

- [x] 3.1 Run strict target, capability and all OpenSpec validation before and
  after spec synchronization.
- [x] 3.2 Parse `.mcp.json` with `python3 -m json.tool` and
  `.codex/config.toml` with Python `tomllib`; run current-only
  `python3 scripts/public-surface-scan.py` and
  `bin/changerail-source-classification --workspace . --json check`.
- [x] 3.3 Run exact authorization/reciprocal-lineage oracle, `git diff --check`
  and explicit whitespace checks over untracked artifacts; do not run history,
  full-release or live commands.
- [x] 3.4 Derive and scope-check the ignored delivery manifest, then run
  normalized review preflight and confirm ordinary/high routing, zero added
  executable LOC and no executable authority/wire-protocol addition.
- [x] 3.5 Sync the release-CI delta, archive only after checks pass and leave the
  authorization card in `3.inprogress` ready for independent review.
