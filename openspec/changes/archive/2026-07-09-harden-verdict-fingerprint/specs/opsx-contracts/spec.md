## MODIFIED Requirements

### Requirement: Review verdict fingerprint
OPSX MUST provide a deterministic helper command that computes the review
freshness fingerprint from git HEAD, status, tracked diff and untracked
non-ignored file content.

#### Scenario: Reviewer writes a verdict
- **WHEN** reviewer runs `bin/opsx-review-verdict fingerprint --workspace .`
- **THEN** the helper emits JSON containing the current head commit and
  `sha256:<hex>` diff fingerprint

#### Scenario: Untracked deliverable content changes
- **WHEN** an untracked non-ignored file's content changes without changing its
  path
- **THEN** the helper emits a different `sha256:<hex>` diff fingerprint

#### Scenario: Ignored runtime content changes
- **WHEN** an ignored file such as `.runtime/opsx/reviews/<card-id>.json` is
  added or changed
- **THEN** the helper emits the same `sha256:<hex>` diff fingerprint for the
  otherwise unchanged working tree
