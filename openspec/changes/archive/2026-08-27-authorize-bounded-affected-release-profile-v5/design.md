## Context

Published rescue commit `ab23b7c8cfafd1b031b669a9a07667e135efd603`
exhausts terminal affected v4 and defines one clean v5 path. This change is the
separate authorization gate between that decision and any v5 card, focused test
or production work.

## Goals / Non-Goals

**Goals:**

- Bind one exact v5 implementation successor and bounded LOC allowance.
- Preserve exact dependency and sole-block relations.
- Carry the retained pre-production RED and reviewer reconstruction boundary.
- Preserve every published affected v4 behavioral and connected-proof invariant.

**Non-Goals:**

- Creating or implementing the v5 successor.
- Reading or importing terminal v4 implementation artifacts.
- Running history, real full/affected, benchmark, live or certification checks.

## Decisions

### Exact authorization

The authorization starts from exact published rescue HEAD and contains one
investigation object:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md","investigation_id":"rescue-affected-release-profile-red-evidence-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v5.md","successor_id":"implement-bounded-affected-release-profile-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on the rescue decision, integration decision, scheduler v1
and v4 authorization, and blocks only v5 implementation. The implementation
will use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md","authorization_id":"authorize-bounded-affected-release-profile-v5"}
```

It starts from authorization-publishing HEAD, depends on those four predecessors
plus this authorization, blocks only certification and adds at most 499
production LOC.

### Auditable test-first ordering

Before its first production, CI or main-spec mutation, v5 may create only its
card, same-slug OpenSpec and focused-test artifacts. It then invokes
`bin/changerail-evidence capture` around one command that first emits
`bin/changerail-review-verdict fingerprint --workspace .` and then runs the
focused test without masking its non-zero result.

The evidence entry must be `failed`, retain a non-zero exit code and reference
raw output containing `tree_sha`, `diff_fingerprint` and a concrete missing
production symbol/module error. A later reproduction cannot replace it.

The fresh reviewer reconstructs the saved Git tree object, diffs it against the
authorization HEAD and rejects any pre-RED production, CI or main-spec change.
Missing object reachability, a successful wrapper or an unrelated failure is
`NO-GO`.

### Published behavioral floor

V5 reconstructs from published sources and preserves exact 35→30 ownership,
aggregate admission, strict four-stream selection, typed scheduler output,
full-only authority, source-safe CI, connected resolved-base counterfactuals
and protocol-artifact non-authority. Terminal v4 artifacts remain unread and
cannot satisfy any gate.

## Risks / Trade-offs

- [Authorization is treated as implementation closure] -> Successor paths and
  executable changes remain absent until this card is published.
- [RED failure is masked] -> Evidence requires non-zero capture status and a
  specific missing-symbol/module error.
- [Fingerprint occurs after forbidden mutation] -> Reviewer reconstructs and
  compares the saved tree against exact authorization HEAD.
- [Ignored evidence is lost] -> Lost mandatory RED evidence requires another
  clean lineage; later reproduction is insufficient.

## Migration Plan

1. Publish this docs-only authorization from exact rescue HEAD.
2. Create the sole v5 implementation from the authorization-publishing HEAD.
3. Retain and audit valid RED before production mutation.
4. Complete implementation review and later certification separately.

Rollback is omission of this unpublished authorization; published history is
not rewritten.

## Open Questions

None.
