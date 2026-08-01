## ADDED Requirements

### Requirement: Delivery manifest scope reconciliation
Delivery manifest helpers MUST provide a schema-backed `scope-check` command
that compares manifest `committable_paths` with actual Git scope for the
working tree, the staged index or both targets.

#### Scenario: Working-tree scope matches manifest
- **WHEN** `scripts/changerail_delivery_manifest.py scope-check --target working-tree --json` checks a manifest whose committable operations match the current non-ignored working-tree status
- **THEN** the helper exits zero
- **AND** the JSON result reports `ok: true` for the working-tree target

#### Scenario: Staged scope matches manifest
- **WHEN** `scripts/changerail_delivery_manifest.py scope-check --target staged --json` checks a manifest whose committable operations match the staged index
- **THEN** the helper exits zero
- **AND** the JSON result reports `ok: true` for the staged target

#### Scenario: Manifest scope has missing, extra and mismatched paths
- **WHEN** scope reconciliation finds a path claimed by the manifest but absent from the target, a target path absent from the manifest or a path whose operation differs
- **THEN** the helper exits non-zero
- **AND** the JSON result lists those differences under `missing`, `extra` and `mismatched` entries for the checked target

#### Scenario: Runtime paths are excluded from committable scope
- **WHEN** ignored runtime manifest, verdict or review-history paths exist during scope reconciliation
- **THEN** the helper excludes those paths from actual committable scope
- **AND** it does not require runtime paths to appear in `committable_paths`

### Requirement: NUL-safe operation-aware scope comparison
Delivery manifest scope reconciliation MUST use machine-readable NUL-delimited
Git data and MUST compare add, modify, delete and rename operations without
lossy path parsing.

#### Scenario: Scope contains add modify delete and rename operations
- **WHEN** a manifest and target Git state contain additions, modifications, deletions and renames
- **THEN** scope reconciliation compares each operation type explicitly
- **AND** rename comparison uses source and target paths rather than a
  human-formatted arrow string

#### Scenario: Scope contains paths requiring byte-preserving round trip
- **WHEN** a target path contains spaces, quotes, Unicode, literal arrow text or valid non-UTF-8 bytes on Linux
- **THEN** scope reconciliation preserves the repository-relative path bytes through filesystem encoding round trip
- **AND** it does not split or quote paths through shell-oriented parsing

### Requirement: Delivery manifest handoff summaries
Delivery manifests MUST support concise machine-readable handoff summaries for
verification evidence, independent review outcome and final board-card state.

#### Scenario: Delivery records verification summary
- **WHEN** delivery updates the manifest after running verification
- **THEN** the manifest can record a concise `verification_summary` containing a result, short summary text and command/evidence references
- **AND** raw command logs remain outside the manifest in ignored runtime evidence

#### Scenario: Review records handoff summary
- **WHEN** independent review writes or validates a verdict for a delivered card
- **THEN** the manifest can record a concise `review_summary` containing the verdict result, review cycle, finding counts and verdict path
- **AND** the latest canonical verdict remains `.runtime/changerail/reviews/<card-id>.json`

#### Scenario: Publish records final card state
- **WHEN** publish finalizes a reviewed board card
- **THEN** the manifest can record `final_card_state` with the final card path, status and stable result summary
- **AND** exact mutable publish details remain in the manifest publish ledger instead of tracked card text

### Requirement: Scope-check smoke coverage
ChangeRail smoke tests MUST cover delivery manifest scope reconciliation,
including negative staged-scope cases that would otherwise produce a false
green publish.

#### Scenario: Extra staged path is rejected
- **WHEN** a staged file is not listed in manifest `committable_paths`
- **THEN** the scope-check smoke observes non-zero helper output
- **AND** the diagnostic lists the staged file under `extra`

#### Scenario: Missing staged path is rejected
- **WHEN** a manifest committable path is not present in the staged index
- **THEN** the scope-check smoke observes non-zero helper output
- **AND** the diagnostic lists the manifest path under `missing`
