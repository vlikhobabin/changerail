## MODIFIED Requirements

### Requirement: Review verdict fingerprint
ChangeRail MUST provide a deterministic helper command that computes the review
freshness fingerprint and reviewed tree SHA from git HEAD, status, tracked diff
and untracked non-ignored file content. The helper MUST compute the exact
reviewed tree from a machine-readable changed path set without a full-index
refresh when Git can represent the current workspace changes safely.

#### Scenario: Reviewer writes a verdict
- **WHEN** reviewer runs `bin/changerail-review-verdict fingerprint --workspace .`
- **THEN** the helper emits JSON containing the current head commit and
  `sha256:<hex>` diff fingerprint
- **AND** it emits a 40-hex `tree_sha` for the exact reviewed tree

#### Scenario: Untracked deliverable content changes
- **WHEN** an untracked non-ignored file's content changes without changing its
  path
- **THEN** the helper emits a different `sha256:<hex>` diff fingerprint
- **AND** it emits a different `tree_sha`

#### Scenario: Ignored runtime content changes
- **WHEN** an ignored file such as `.runtime/changerail/reviews/<card-id>.json` is
  added or changed
- **THEN** the helper emits the same `sha256:<hex>` diff fingerprint for the
  otherwise unchanged working tree
- **AND** it emits the same `tree_sha`

#### Scenario: Publish detects reviewed tree drift
- **WHEN** `bin/changerail-review-verdict validate --check-fresh` checks a
  verdict whose `workspace.tree_sha` differs from the current reviewed tree
- **THEN** validation fails before publish can stage files

#### Scenario: Docs-only payload avoids full-index refresh
- **WHEN** a large repository has a docs-only working-tree payload and Git
  reports an exact changed path set
- **THEN** the helper computes the reviewed tree by applying only that changed
  path set to a temporary index
- **AND** it does not run full-repository `git add -A` for the happy path

#### Scenario: Optimized tree matches reference tree for path edge cases
- **WHEN** the workspace contains additions, modifications, deletions, renames,
  symlinks, Unicode paths, spaces, literal ` -> ` text or valid non-UTF-8 Linux
  paths
- **THEN** the optimized reviewed-tree builder emits the same `tree_sha` and
  `diff_fingerprint` as the reference full-tree algorithm

#### Scenario: Unsafe path state does not produce approximate freshness
- **WHEN** Git reports a changed path set that the optimized builder cannot
  represent exactly
- **THEN** the helper either uses the reference full-tree algorithm or exits
  non-zero before emitting freshness data
