## Why

Before ChangeRail can reproduce Windows wiring failures, it needs a sanitized
baseline for the two operator-managed native Windows hosts. The public result
must prove SSH/non-interactive execution, safe fixture transfer and disposable
workspace readiness without exposing private host identities or paths.

## What Changes

- Capture a two-host support matrix for OS/filesystem/Git/Python/shell and
  privilege capabilities using only generic host ids.
- Retain raw command output under ignored `.runtime/changerail/evidence/` and
  publish only concise sanitized outcomes.
- Check SSH access, non-interactive command execution, safe fixture transfer and
  disposable test root setup for both hosts.
- Add a public compatibility note that identifies current native Windows lab
  readiness and the evidence retention boundaries.

## Capabilities

### New Capabilities
- `changerail-windows-support-matrix`: sanitized two-host capability matrix and
  evidence contract for native Windows research readiness.

### Modified Capabilities
- none

## Impact

- `docs/compatibility.md` gains the current sanitized Windows lab readiness
  matrix.
- Runtime evidence is retained only in ignored `.runtime/changerail/evidence/`.
- The result becomes input evidence for `030-02` and `030-03`; it does not
  change ChangeRail runtime or bootstrap behavior.
