## Why

Architecture and instruction checks are consumer-owned, but ChangeRail needs a
safe generic ingestion boundary so external native checkers cannot silently
produce false green maintenance scan results.

## What Changes

- Extend maintenance scan with an adapter detector that invokes configured argv
  arrays without shell expansion from the repository cwd.
- Add timeout, exit-code and JSON-output handling that turns adapter failure,
  timeout, invalid output or path escape into detector-error findings.
- Define the adapter output contract through the existing scan report and
  detector-result schemas instead of embedding language-specific analyzers in
  ChangeRail core.
- Add fixtures for successful adapter findings, timeout, invalid JSON, failed
  adapter process and unsafe paths.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: adds generic architecture/instruction
  adapter execution semantics to repository maintenance scan.
- `changerail-contracts`: documents the detector-result fields used by adapter
  findings and detector errors.

## Impact

- Affected code: `scripts/changerail_maintenance.py`,
  `scripts/changerail_repository_knowledge.py` and focused fixture helpers.
- Affected contracts/docs: maintenance policy optional adapter configuration,
  scan report/result schemas and `docs/changerail-contracts.md`.
- No new runtime dependency on ArchUnit or another language-specific checker;
  adapters remain consumer-supplied executables.
