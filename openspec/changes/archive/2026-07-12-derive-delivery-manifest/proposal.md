# derive-delivery-manifest

## Why

Delivery manifests are required review/publish handoff evidence, but broad cards
currently require manual path enumeration. Manual manifests are easy to make
incomplete or inconsistent with `git status`.

## What Changes

- Extend `scripts/changerail_delivery_manifest.py` with a derive/update command.
- Derive card metadata, ordered changes, archived paths and dirty-tree
  committable paths from a board card and workspace status.
- Preserve existing `validate` and `staging-plan` behavior.

## Impact

- Affects delivery manifest helper and potentially publish/review handoff.
- Updates `changerail-contracts` specification.
