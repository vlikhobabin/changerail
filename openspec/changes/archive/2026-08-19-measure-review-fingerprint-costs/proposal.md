## Why

Review fingerprint latency is currently opaque: field validation showed that a
docs-only payload in a large generated-source repository spent most review gate
time inside full-tree fingerprint/preflight work, but ChangeRail does not expose
which sub-step dominates. Before optimizing the algorithm, the toolchain needs a
public-safe benchmark and timing breakdown that can prove the bottleneck and
guard against regressions.

## What Changes

- Add focused timing instrumentation for review fingerprint/preflight phases:
  changed path discovery, temporary reviewed-tree construction, untracked
  content hashing, strict OpenSpec validation, scoped diff whitespace check and
  public-surface scan.
- Add a synthetic large-repository benchmark that creates generic tracked
  source and docs payloads without storing private consumer data.
- Record baseline and threshold data in deterministic smoke output so follow-up
  optimization changes can compare before/after behavior.
- Keep existing freshness semantics and helper output unchanged in this change.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: review fingerprint and review preflight expose
  public-safe timing breakdowns and synthetic benchmark coverage.

## Impact

- Affected files: `scripts/changerail_review_verdict.py`,
  `scripts/changerail_review_preflight.py`, focused smoke/benchmark scripts,
  release baseline wiring and OpenSpec contract artifacts.
- Public helper freshness fields stay compatible: `head_commit`, `tree_sha` and
  `diff_fingerprint` retain their existing meanings.
- No consumer repository names, raw field-validation logs or private paths are
  tracked.
