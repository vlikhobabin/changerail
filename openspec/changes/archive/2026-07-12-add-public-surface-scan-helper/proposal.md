# add-public-surface-scan-helper

## Why

Public-surface scans are required before commits, but current scans are ad hoc
shell commands. They can fail on regex portability and do not centralize
allowlists for generic examples or historical rename references.

## What Changes

- Add `scripts/public-surface-scan.py`.
- Support explicit path scans and default public-surface scans.
- Add a self-test/negative fixture for disallowed `/opt/<private>` paths.

## Impact

- Affects public-safety verification workflow.
- Updates `changerail-agent-methodology` specification.
