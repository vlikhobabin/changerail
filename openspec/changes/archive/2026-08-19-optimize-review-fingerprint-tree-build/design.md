## Context

`compute_reviewed_tree()` currently creates a temporary index, optionally reads
HEAD into it and runs `git add -A` for the whole repository before
`git write-tree`. This is correct but expensive because Git must refresh every
tracked path. The delivery manifest helper already uses NUL-delimited Git data
for exact path handling; the fingerprint helper should use the same discipline
for path-scoped tree construction.

## Goals / Non-Goals

Goals:
- Compute the same reviewed tree SHA as the existing reference algorithm.
- Bound normal docs-only cost to the exact changed path set.
- Preserve byte-safe path handling for Git paths, including non-UTF-8 Linux
  names.
- Keep ignored runtime files out of the fingerprint and reviewed tree.

Non-Goals:
- Weaken freshness validation or compare only manifest paths.
- Require users to stage payloads before review.
- Introduce project-specific exclusions for generated source.
- Change review verdict schema fields.

## Decisions

1. Keep the full-tree implementation as an internal reference/fallback used by
   tests and by runtime when path-scoped construction cannot safely proceed.
2. Derive the changed path set from NUL-delimited Git status data rather than
   porcelain text intended for humans. For renames, include both source and
   target paths so the temporary index removes and adds the right entries.
3. Initialize the temporary index from HEAD, then apply path-scoped updates:
   - tracked modifications and additions through path-limited index update;
   - deletions through path-limited index removal;
   - untracked non-ignored regular files and symlinks through explicit add;
   - ignored runtime files through Git exclude handling so they never enter the
     candidate set.
4. Treat unsafe states conservatively. If a changed path is a directory that
   cannot be expanded into exact files, a path disappears during processing, or
   Git reports a status shape the helper does not understand, use the reference
   algorithm or fail with an input error rather than emitting an approximate
   tree.
5. Add parity tests that compare optimized and reference results for add,
   modify, delete, rename, symlink, Unicode, spaces, literal arrow and valid
   non-UTF-8 Linux paths.

## Verification

- Extend `scripts/smoke-review-fingerprint.py` with reference-versus-optimized
  parity checks for all accepted path classes.
- Add a negative/edge smoke for unsupported or racing path states if practical.
- Run the synthetic large-repository benchmark from
  `measure-review-fingerprint-costs` and confirm docs-only tree construction no
  longer performs a full-index refresh on the happy path.
- Run review verdict validation smoke, review preflight smoke, strict OpenSpec
  validation and whitespace checks.
