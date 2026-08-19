# Deliver bounded review fingerprint optimization

## Status
1.backlog

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
- `openspec/board/1.backlog/investigate-bounded-review-fingerprint-payload.md`
- `openspec/board/1.backlog/authorize-bounded-review-fingerprint-payload.md`

## Result
not started

## Next
- `$chrl-ff openspec/board/1.backlog/deliver-bounded-review-fingerprint-optimization.md`

## Log
- 2026-08-19T07:17:52Z created as the bounded replacement for the retained
  implementation that exceeded the maximum authorization ceiling.
