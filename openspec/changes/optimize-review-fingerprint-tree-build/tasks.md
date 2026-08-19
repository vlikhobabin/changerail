## 1. Canonical Tree Builder

- [ ] 1.1 Refactor review fingerprint code so the reference full-tree builder is
  callable by tests and fallback paths.
- [ ] 1.2 Add a NUL-safe changed path model for modify, add, delete, rename,
  untracked regular file and symlink states.
- [ ] 1.3 Implement path-scoped temporary-index updates that produce the exact
  reviewed tree SHA from HEAD plus the changed path set.
- [ ] 1.4 Preserve ignored runtime exclusions and untracked content hashing.

## 2. Parity And Performance Coverage

- [ ] 2.1 Extend fingerprint smoke coverage for add, modify, delete, rename,
  symlink, Unicode, spaces, literal arrow and valid non-UTF-8 Linux paths.
- [ ] 2.2 Assert optimized and reference builders produce identical
  `tree_sha` and `diff_fingerprint` values for the covered path classes.
- [ ] 2.3 Run the synthetic large-repository benchmark and record the docs-only
  before/after behavior.

## 3. Verification

- [ ] 3.1 Run `python3 -m py_compile scripts/changerail_review_verdict.py`.
- [ ] 3.2 Run `python3 scripts/smoke-review-fingerprint.py`.
- [ ] 3.3 Run `python3 scripts/smoke-review-verdict-validation.py`.
- [ ] 3.4 Run `python3 scripts/smoke-review-preflight.py`.
- [ ] 3.5 Run the synthetic large-repository benchmark smoke.
- [ ] 3.6 Run `./bin/openspec validate "optimize-review-fingerprint-tree-build" --strict`.
- [ ] 3.7 Run `./bin/openspec validate --all --strict`.
- [ ] 3.8 Run `git diff --check`.
