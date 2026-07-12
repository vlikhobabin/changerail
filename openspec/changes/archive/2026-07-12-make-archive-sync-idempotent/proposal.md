# make-archive-sync-idempotent

## Why

`openspec archive` can abort with duplicate `ADDED Requirements` when main specs
were already synced manually before archiving. In the observed case the wrapper
returned a successful shell status while the CLI printed that no files were
changed. That makes delivery automation brittle and forces operators to know
when `--skip-specs` is appropriate.

## What Changes

- Add wrapper-level detection for the duplicate already-synced archive abort.
- Make the failure explicit and diagnostic when automatic idempotent archive is
  not safe.
- Add smoke coverage for duplicate requirement archive diagnostics.

## Impact

- Affects `bin/openspec` wrapper behavior for `archive`.
- Adds verification under `scripts/`.
- Updates `changerail-openspec-lifecycle` specification.
