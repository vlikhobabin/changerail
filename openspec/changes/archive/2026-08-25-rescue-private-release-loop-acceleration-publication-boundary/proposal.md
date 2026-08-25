## Why

Private multi-worktree integration proved that ChangeRail can keep an
authoritative full gate while reducing ordinary affected verification to a
small non-authoritative subset. That aggregate branch cannot be published:
its ancestry activated dormant A1 before the separately published A2 boundary,
and its local PASS evidence is not an atomic payload-bound public receipt.

A clean public decision is required before implementation. It must preserve
the validated architecture findings without cherry-picking private commits,
split the executable scope below the repository's `500`-LOC authorization
limit, and make parallel work safe only where ownership is independent.

## What Changes

- Replace the old mandatory A1 -> A2 -> scanner -> Windows ordering for one new
  clean lineage with four bounded owners: structural history, isolated cases,
  public registry/affected profile, and payload-bound terminal authority.
- Allow the history and isolation foundations to run in parallel after this
  decision is published; require registry/profile and terminal authority to
  follow in order.
- Bind exact future authorization objects, LOC ceilings, protocol allowances,
  clean predecessor rules and deterministic proof boundaries.
- Require bounded semantic execution, per-step telemetry and diagnostics,
  atomic payload-bound receipts, manifest/review/publish equality and one
  canonical full-release CI entrypoint.
- Defer measured bottleneck optimization and native Windows certification to
  explicit downstream work after the authority core is published.
- Keep private commits, diffs, runtime logs and evidence forensic-only and
  inadmissible for public review or publication.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: supersede the exhausted publication order with a
  clean bounded acceleration lineage and precise authority/evidence gates.

## Impact

This change affects only the board card and OpenSpec release-CI contract. It
adds no executable, test or runtime code, performs no history/full/live gate,
and changes no consumer-project behavior. Public examples and paths remain
generic.
