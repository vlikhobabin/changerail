## Why

Source profile materialization/checks меняют classification protocol и требуют
exact bounded authorization.

## What Changes

- Bind ceiling 500/protocol allowance to exact source-profile successor.
- Preserve one effective rules source/normalizer and mismatch rejection.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: exact source-profile authorization source.

## Impact

Board/OpenSpec contract и non-production preflight evidence only.
