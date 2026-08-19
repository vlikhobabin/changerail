# Deliver bounded review fingerprint optimization

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- `openspec/board/5.canceled/optimize-review-fingerprint-for-large-repositories.md`
- `investigate-bounded-review-fingerprint-payload`

## Summary
Deliver the original fingerprint performance scope as one bounded replacement
after published investigation. Preserve exact reviewed-tree and cache freshness
semantics while keeping the replacement at or below the authorized 500 added
production LOC ceiling.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-review-fingerprint-payload.md","authorization_id":"authorize-bounded-review-fingerprint-payload"}`

## Depends On
- `investigate-bounded-review-fingerprint-payload`
- `authorize-bounded-review-fingerprint-payload`

## Acceptance
- Timing diagnostics separate changed-path discovery, reviewed-tree
  construction, untracked hashing, OpenSpec validation, whitespace and public
  scan costs without exposing raw repository content.
- Safe happy paths build the exact reviewed tree from HEAD plus a NUL-safe
  changed-path set without a full-repository `git add -A`.
- Tree SHA and diff fingerprint retain parity for add, modify, delete, rename,
  symlink, Unicode, spaces, literal arrow and valid non-UTF-8 Linux paths.
- Untracked regular files remain content-bound and ignored runtime files remain
  excluded.
- A validated ignored cache is reused only for an unchanged exact payload and
  invalidates on tracked, untracked, deletion and permission changes.
- Preflight, verdict validation and publish share the canonical fingerprint
  implementation and retain fail-closed fallback behavior.
- Synthetic benchmark and focused cache/parity smokes pass without private
  fixtures or consumer paths.
- Deterministic preflight reports at most 500 added production LOC, validates
  the exact published authorization and routes the payload to one independent
  ordinary `high` review.

## Non-Goals
- Weakening freshness, scope or independent review gates.
- Raising the global complexity limit or authorization ceiling.
- Dropping focused edge-path or cache invalidation coverage to meet the bound.

## Change Set
- `measure-review-fingerprint-costs`
- `optimize-review-fingerprint-tree-build`
- `share-review-fingerprint-preflight-cache`

## Verify
- `python3 scripts/smoke-review-fingerprint.py`
- `python3 scripts/smoke-review-verdict-validation.py`
- `python3 scripts/smoke-review-preflight.py`
- focused synthetic benchmark and cache smoke created by the changes
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-release-ci.py`
- `./bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/measure-review-fingerprint-costs/`
- `openspec/changes/optimize-review-fingerprint-tree-build/`
- `openspec/changes/share-review-fingerprint-preflight-cache/`
- `openspec/board/2.todo/investigate-bounded-review-fingerprint-payload.md`
- `openspec/board/2.todo/authorize-bounded-review-fingerprint-payload.md`

## Result
planned

## Next
- Complete and publish `investigate-bounded-review-fingerprint-payload`.
- Complete and publish `authorize-bounded-review-fingerprint-payload`.
- `$chrl-do openspec/board/2.todo/deliver-bounded-review-fingerprint-optimization.md`

## Change 1: `measure-review-fingerprint-costs`

### Why
Before changing the fingerprint algorithm, maintainers need public-safe timing
evidence that separates full-tree setup from changed-scope and non-fingerprint
preflight work.

### Goal
Add opt-in diagnostics and synthetic benchmark coverage that measure review
fingerprint and deterministic preflight costs without changing canonical
freshness values.

### Scope
- Timing diagnostics for changed-path discovery, reviewed-tree construction,
  untracked hashing, OpenSpec validation, scoped whitespace checks and
  public-surface scans.
- Synthetic large-repository benchmark coverage for docs-only and source
  payloads using generic temporary repositories.
- Public-safe benchmark output and threshold rationale for later comparison.

### Acceptance
- Diagnostics separate changed-path discovery, reviewed-tree construction,
  untracked content hashing, OpenSpec validation, scoped whitespace check and
  public-surface scan costs.
- Default fingerprint output remains compatible and retains the same
  `head_commit`, `tree_sha` and `diff_fingerprint` meanings.
- Benchmark fixtures do not store private consumer paths, field-validation logs
  or generated repository contents in tracked files.

### Depends On
- none

### Related
- `openspec/changes/measure-review-fingerprint-costs/`

## Change 2: `optimize-review-fingerprint-tree-build`

### Why
The reference full-repository `git add -A` tree build is exact but too expensive
for small payloads in large tracked trees.

### Goal
Build the exact reviewed tree from HEAD plus a NUL-safe changed-path set on the
safe happy path, while retaining reference parity and fail-closed fallback.

### Scope
- Canonical reviewed-tree builder with a retained full-tree reference/fallback.
- NUL-safe changed-path model for add, modify, delete, rename, untracked
  regular file and symlink states.
- Path-scoped temporary-index updates and focused reference-parity smokes.
- Preservation of ignored runtime exclusions and untracked content hashing.

### Acceptance
- Safe docs-only payloads in large repositories avoid full-repository
  `git add -A` when Git reports an exact changed-path set.
- `tree_sha` and `diff_fingerprint` match the reference full-tree algorithm for
  add, modify, delete, rename, symlink, Unicode, spaces, literal arrow and valid
  non-UTF-8 Linux paths.
- Unsafe path states use the reference algorithm or exit non-zero before
  emitting approximate freshness data.

### Depends On
- `measure-review-fingerprint-costs`

### Related
- `openspec/changes/optimize-review-fingerprint-tree-build/`

## Change 3: `share-review-fingerprint-preflight-cache`

### Why
After the tree build is exact and changed-scope bounded, delivery still computes
the same payload identity across preflight, verdict validation and publish.

### Goal
Share the canonical fingerprint implementation across review freshness
consumers and reuse an ignored runtime cache only when the current workspace
proves the cached payload is unchanged.

### Scope
- Shared fingerprint implementation for review preflight, verdict validation
  and publish freshness checks.
- Ignored `.runtime/changerail/` cache records with schema/version, HEAD,
  changed-path metadata, `tree_sha` and `diff_fingerprint`.
- Cache hit/miss diagnostics and stale-cache invalidation coverage.

### Acceptance
- Preflight, `validate --check-fresh` and publish observe identical
  `head_commit`, `tree_sha` and `diff_fingerprint` for the same workspace
  state.
- Cache reuse is allowed only after current HEAD, changed-path metadata,
  untracked content metadata and Git exclude state prove the exact payload is
  unchanged.
- Stale, malformed or cross-workspace cache entries recompute or fail closed
  before emitting freshness data.
- The full successor delivery remains at or below 500 added production LOC and
  validates the exact published authorization reference:
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-review-fingerprint-payload.md","authorization_id":"authorize-bounded-review-fingerprint-payload"}`.

### Depends On
- `optimize-review-fingerprint-tree-build`

### Related
- `openspec/changes/share-review-fingerprint-preflight-cache/`

## Log
- 2026-08-19T07:17:52Z created as the bounded replacement for the retained
  implementation that exceeded the maximum authorization ceiling.
- 2026-08-19T07:57:22Z `$chrl-ff` adopted the existing apply-ready changes
  `measure-review-fingerprint-costs`,
  `optimize-review-fingerprint-tree-build` and
  `share-review-fingerprint-preflight-cache`, preserved the exact published
  authorization reference and moved the card to `2.todo`.
