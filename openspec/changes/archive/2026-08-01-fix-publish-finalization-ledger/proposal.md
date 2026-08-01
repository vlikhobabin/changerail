## Why

Tracked done-card metadata currently tries to describe the commit that contains
that same metadata, and earlier push-enabled finalization can leave mutable
`pending` push state in public card text. This creates stale or impossible
publication records for consumers that rely on ChangeRail publish evidence.

## What Changes

- Separate reviewed payload commit identity from final published commit identity
  in the ignored delivery manifest ledger.
- Tighten publish finalization so tracked board cards record only stable
  outcome text and do not contain their own exact final commit hash or mutable
  push state.
- Require helper-assisted finalization to update manifest `card.path` and
  `card.status` after the board move.
- Add a focused local bare-remote regression smoke covering commit,
  finalization, amend, push and manifest publish update.
- Update `changerail-pub` guidance so publish records exact remote/branch/status
  metadata in ignored runtime state rather than tracked card text.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: delivery manifest publish ledger fields and helper
  behavior distinguish payload and published commits.
- `changerail-agent-methodology`: post-publish card finalization keeps tracked
  card metadata stable and shifts exact mutable publication details to ignored
  runtime evidence.
- `changerail-skill-surface`: `changerail-pub` contract finalizes board
  metadata without introducing stale exact commit or pending push text into
  tracked cards.

## Impact

- `schemas/changerail-delivery-manifest.schema.json`
- `scripts/changerail_delivery_manifest.py`
- `scripts/smoke-delivery-manifest-derive.py` and focused publish/finalization
  smoke coverage
- `skills/changerail-pub/SKILL.md`
- `skills/changerail-do/references/changerail-delivery-manifest.md`
- `AGENTS.shared.md`, board/publish docs and synced OpenSpec specs
