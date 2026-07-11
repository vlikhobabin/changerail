## 1. Lifecycle Contract

- [x] 1.1 Update shared methodology and how-it-works docs to state archive-before-review and done-after-publish lifecycle.
- [x] 1.2 Update `opsx-do`, `opsx-pub` and `opsx-deliver` skill contracts to preserve `3.inprogress` until publish and invalidate substantive post-`go` changes.
- [x] 1.3 Update delivery manifest reference docs with file operation semantics for add, modify, delete and rename.

## 2. Manifest Contract

- [x] 2.1 Extend `schemas/opsx-delivery-manifest.schema.json` with optional structured operation fields.
- [x] 2.2 Add a delivery-manifest helper that validates manifests and reports staging paths for move/delete operations.
- [x] 2.3 Add smoke coverage proving a board-card rename includes both source and target paths in the staging proposal.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-delivery-manifest.py`.
- [x] 3.2 Run `./bin/openspec validate harden-delivery-lifecycle-contract --strict`.
- [x] 3.3 Run `git diff --check`.
