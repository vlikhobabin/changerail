## Context

`010-03` introduced a delivery manifest ledger that can describe add, modify,
delete and rename operations and keep mutable publish details in ignored
runtime state. Publish and review still need a deterministic way to compare that
claimed scope with Git's actual working tree and staged index before staging or
publishing. The helper already reads NUL-delimited porcelain status for manifest
derivation, so the new reconciliation behavior should reuse that source of
truth instead of adding text parsing around `git diff --name-only`.

The handoff summary must remain concise. Raw command output, logs and review
history stay in ignored runtime files; the manifest should keep only short
operator-facing summaries that can be validated and audited.

## Goals / Non-Goals

**Goals:**
- Add a `scope-check` helper command that compares manifest scope with
  working-tree status and staged index status.
- Preserve NUL-safe handling and operation-aware comparison for add, modify,
  delete and rename operations.
- Report missing, extra and mismatched paths in machine-readable output.
- Extend the delivery manifest schema with concise `verification_summary`,
  `review_summary` and `final_card_state` handoff objects.
- Cover false-green cases with focused positive and negative smokes, including
  extra staged paths.

**Non-Goals:**
- Capture or store raw verification command logs in the manifest.
- Add a generic evidence capture system for every command.
- Replace review verdict or review-cycle history contracts.

## Decisions

1. `scope-check` will compare normalized operation entries, not path-only sets.
   The expected side comes from `committable_paths`; the actual side comes from
   NUL-delimited `git status --porcelain=v1 -z` for working tree and
   `git diff --cached --name-status -z` for staged state. This keeps rename and
   delete intent visible.

2. Reconciliation will support separate `--target working-tree`, `--target
   staged` and `--target both` modes, with `both` as the default. Publish can
   fail before staging when working-tree scope does not match, then fail again
   after explicit staging if the index contains extra or missing paths.

3. Ignored runtime paths will be excluded from actual committable scope before
   comparison. The exclusion uses manifest `excluded_runtime_paths` and Git's
   ignored-file behavior, so runtime manifest/verdict files do not force
   manual overrides.

4. The helper output will include `ok`, per-target `missing`, `extra` and
   `mismatched` arrays and a concise diagnostic. Non-zero exit is required when
   any target has a mismatch. Human-readable output may be compact, but JSON is
   the contract used by review and publish gates.

5. Handoff summaries will be small schema-backed objects in the manifest:
   `verification_summary`, `review_summary` and `final_card_state`. They record
   result/status, short summary text and optional references to ignored evidence
   paths or public card/archive paths, but they do not duplicate raw logs.

## Risks / Trade-offs

- Operation normalization may initially cover only Git operations ChangeRail
  already claims. Mitigation: reject unknown or incomplete operation entries
  rather than silently treating them as path-only matches.
- Staged rename detection depends on Git rename detection. Mitigation: use
  `git diff --cached --name-status -z --find-renames` and allow delete/add
  mismatches to be reported explicitly when Git does not classify a pair as a
  rename.
- Handoff summaries can drift into raw-log storage. Mitigation: schema fields
  remain concise strings and bounded arrays of references, while raw evidence
  stays in ignored runtime paths.
