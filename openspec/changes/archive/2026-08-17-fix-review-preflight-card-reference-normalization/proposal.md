## Why

The new published-investigation authorization check rejects valid existing
board references because published cards often use backticked `<id>.md` rather
than a bare id.

## What Changes

- Normalize exact bare ids, filenames and canonical board paths before relation
  comparison.
- Keep non-board paths, foreign stems and malformed/ambiguous values as
  non-matches.
- Add focused smoke coverage and clarify the accepted forms in the contract.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: published-investigation relation validation accepts
  only exact equivalent card reference forms.

## Impact

One Python matcher, its focused smoke and the deterministic preflight contract.
No CLI, authority, runtime or model-launch change.
