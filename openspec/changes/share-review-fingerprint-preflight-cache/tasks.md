## 1. Shared Fingerprint Surface

- [ ] 1.1 Refactor callers so review preflight, verdict validation and publish
  freshness checks use the same canonical fingerprint function.
- [ ] 1.2 Remove or prevent duplicate freshness logic in wrapper/publish paths.
- [ ] 1.3 Ensure diagnostics report whether freshness was recomputed or reused.

## 2. Cache Semantics

- [ ] 2.1 Add ignored runtime cache records with schema/version, HEAD,
  changed-path metadata fingerprint, `tree_sha` and `diff_fingerprint`.
- [ ] 2.2 Validate cache hits against current HEAD, changed path metadata,
  untracked content metadata and Git exclude state before reuse.
- [ ] 2.3 Fail closed or recompute on stale, malformed or cross-workspace cache
  entries.

## 3. Verification

- [ ] 3.1 Add smoke coverage for repeated unchanged preflight cache reuse.
- [ ] 3.2 Add negative smoke coverage for tracked modify, delete, rename,
  untracked content and exclude-state cache invalidation.
- [ ] 3.3 Run `python3 -m py_compile scripts/changerail_review_verdict.py scripts/changerail_review_preflight.py`.
- [ ] 3.4 Run `python3 scripts/smoke-review-fingerprint.py`.
- [ ] 3.5 Run `python3 scripts/smoke-review-preflight.py`.
- [ ] 3.6 Run focused cache smoke.
- [ ] 3.7 Run `./bin/openspec validate "share-review-fingerprint-preflight-cache" --strict`.
- [ ] 3.8 Run `./bin/openspec validate --all --strict`.
- [ ] 3.9 Run `git diff --check`.
