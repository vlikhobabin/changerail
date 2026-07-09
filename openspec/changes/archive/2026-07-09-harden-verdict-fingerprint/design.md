## Context

`scripts/opsx_review_verdict.py fingerprint` is the source of truth for
review freshness. It currently hashes `git status --porcelain` and
`git diff HEAD --no-color`, so untracked file names affect the fingerprint but
their bytes do not. This is weak for OPSX cards whose deliverable includes new
files that are intentionally not staged before review.

## Goals / Non-Goals

**Goals:**
- Include deterministic untracked non-ignored path and content data in the
  freshness fingerprint.
- Keep ignored runtime paths, including `.runtime/opsx/reviews/*.json`, outside
  the fingerprint.
- Preserve the `sha256:<64 hex>` output format and existing `validate`,
  `--check-fresh` and exit-code contracts.
- Document the stronger behavior in `docs/opsx-contracts.md` and
  `skills/opsx-review/references/opsx-review-verdict.md`.

**Non-Goals:**
- Change the review verdict schema.
- Require reviewers or publishers to stage files before review.
- Hash ignored files or runtime evidence.
- Introduce external Python dependencies.

## Decisions

1. Enumerate untracked files with `git ls-files --others --exclude-standard`.
   This reuses Git's ignore handling and keeps consumer-project `.gitignore`
   policy authoritative.
2. Sort paths lexically before hashing. Git output is usually stable, but an
   explicit sort makes determinism part of the helper behavior.
3. Hash each untracked file as structured bytes: path marker, UTF-8 path,
   content marker, and raw file bytes. Raw bytes avoid text decoding failures
   for binary files.
4. Skip paths that are no longer regular files by recording a deterministic
   marker. This handles races where an untracked path is removed between
   enumeration and read without crashing the helper.
5. Add a smoke script under `scripts/` that creates a temporary Git repository,
   compares fingerprints after untracked-content edits, and confirms ignored
   file writes do not affect the fingerprint.

## Risks / Trade-offs

- Large untracked files increase fingerprint cost. Mitigation: the helper only
  runs at review/publish gates and streams file reads in chunks.
- A file can change while the helper reads it. Mitigation: the fingerprint still
  represents the bytes observed during the command; publish re-checks freshness
  before staging.
- Direct helper tests in a temporary repo can miss integration drift. Mitigation:
  the delivery verification also runs OpenSpec validation and the repository
  baseline whitespace/config checks.
