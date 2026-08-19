## Why

The canonical review fingerprint currently pays for `git add -A` across the
entire repository to compute the reviewed tree. Large repositories with small
payloads need the same exact `tree_sha` and `diff_fingerprint`, but the cost
should be proportional to the machine-readable changed path set whenever Git
can prove that set exactly.

## What Changes

- Replace the full-index refresh path with a canonical reviewed-tree builder
  that starts from HEAD and applies only the exact changed path set when the set
  can be derived safely.
- Preserve the reference reviewed tree and diff fingerprint for additions,
  modifications, deletions, renames, symlinks, spaces, Unicode, literal arrow
  text and valid non-UTF-8 Linux paths.
- Continue hashing untracked regular files by content and excluding ignored
  runtime files.
- Fall back fail-closed to the reference full-tree algorithm only when the
  changed path set cannot be represented safely.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: review fingerprint tree construction is exact,
  NUL-safe and changed-scope bounded when Git exposes a complete changed path
  set.

## Impact

- Affected files: `scripts/changerail_review_verdict.py`,
  `bin/changerail-review-verdict`, focused fingerprint smoke tests and
  OpenSpec contract artifacts.
- Public helper CLI output remains compatible.
- The optimization is internal to ChangeRail core and does not exclude tracked
  generated source from review scope.
