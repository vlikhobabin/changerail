## Context

`scripts/changerail_review_preflight.py` accepts an injected `fingerprint_fn`,
and `scripts/changerail_review_verdict.py validate --check-fresh` recomputes the
same values independently. The delivery pipeline can therefore pay the exact
same fingerprint cost several times for an unchanged payload. The cache must
not become an alternate authority: the canonical implementation remains the
source of truth, and cache reuse is only a fast path for a proven unchanged
workspace.

## Goals / Non-Goals

Goals:
- Share one canonical fingerprint implementation across preflight, verdict
  validation and publish.
- Reuse cached fingerprint data only when current workspace state proves it is
  unchanged.
- Keep cache state ignored, bounded and public-safe.
- Preserve fail-closed behavior for stale verdicts and stale cache entries.

Non-Goals:
- Trust delivery manifests instead of the full Git changed path set.
- Persist cache state in tracked files.
- Skip required OpenSpec validation, scope checks or public-surface scans.
- Change review verdict schema semantics.

## Decisions

1. Introduce a small cache record under ignored `.runtime/changerail/` with
   schema/version, workspace root identity sanitized for local use, HEAD commit,
   changed path metadata fingerprint, reviewed `tree_sha`, `diff_fingerprint`
   and creation time.
2. Validate cache entries by recomputing cheap freshness inputs first: HEAD,
   NUL-safe changed path metadata and untracked metadata sufficient to know
   whether content hashing/tree construction must rerun. If those inputs do not
   match exactly, recompute and replace the cache.
3. Do not use cache entries across repositories, across HEAD changes, after
   ignored configuration changes that affect Git excludes, or when untracked
   file content metadata is insufficient to prove content stability.
4. Keep the default helper behavior deterministic: cache use should be explicit
   or confined to preflight/review/publish paths that write diagnostic evidence
   showing whether the result was recomputed or reused.
5. Publish and verdict validation continue to compare the current canonical
   freshness result with the reviewed verdict values; a cache hit only supplies
   that current result after validation.

## Verification

- Add smoke coverage for cache hit on repeated unchanged preflight.
- Add negative smoke coverage for stale cache after tracked modify, delete,
  rename and untracked content changes.
- Verify `validate --check-fresh`, review preflight and publish-related helper
  calls all report identical freshness values for the same workspace state.
- Run strict OpenSpec validation and whitespace checks.
