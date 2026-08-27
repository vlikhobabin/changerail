## Context

Published investigation commit
`5d6bfe14b498d22f58be303283537c16cd450c07` terminates the unpublished
affected v5 attempt and defines one clean v6 path. This change is the separate
authorization gate between that decision and any v6 card, focused test or
production work.

## Goals / Non-Goals

**Goals:**

- Bind one exact v6 implementation successor and bounded LOC allowance.
- Preserve exact dependency and sole-block relations.
- Carry the retained pre-production RED and reviewer reconstruction boundary.
- Bind pre-mutation runtime-output admission and the complete connected
  selector-bound counterfactual inventory.
- Preserve every published affected behavioral and authority invariant.

**Non-Goals:**

- Creating or implementing the v6 successor.
- Reading or importing terminal unpublished v5 implementation artifacts.
- Running history, real full/affected, benchmark, live or certification checks.

## Decisions

### Exact authorization

The authorization starts from exact published investigation HEAD and contains
one investigation object:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md","investigation_id":"rescue-affected-release-profile-admission-bounds-boundary-v6","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v6.md","successor_id":"implement-bounded-affected-release-profile-v6","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on the investigation decision, integration decision,
scheduler v1 implementation and v5 authorization, and blocks only v6
implementation. The implementation will use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v6.md","authorization_id":"authorize-bounded-affected-release-profile-v6"}
```

It starts from authorization-publishing HEAD, depends on those four
predecessors plus this authorization, blocks only certification and adds at
most 499 production LOC.

Alternative: authorize implementation directly from the investigation card.
This is rejected because it would collapse the separately reviewed lineage and
protocol allowance gate.

### Auditable test-first ordering

Before its first production, CI or main-spec mutation, v6 may create only its
card, same-slug OpenSpec and focused-test artifacts. It then invokes
`bin/changerail-evidence capture` around one command that first emits
`bin/changerail-review-verdict fingerprint --workspace .` and then runs the
focused test without masking its non-zero result.

The evidence entry must be `failed`, retain a non-zero exit code and reference
raw output containing `tree_sha`, `diff_fingerprint` and a concrete missing
production symbol/module error. The saved tree must remain reachable before
production mutation; a later reproduction cannot replace it.

The fresh reviewer reconstructs that tree against the authorization HEAD and
rejects any pre-RED production, CI or main-spec change. Missing object
reachability, a successful wrapper or an unrelated failure is `NO-GO`.

Alternative: accept a later reproduction bound only to the current diff. This
is rejected because it cannot prove test-first chronology.

### Admission and connected-proof floor

Future v6 performs runtime-output admission before selection, scheduling or any
filesystem creation. Both the leaf and nearest existing parent are bounded and
repository-local. Existing files, symlinks, wrong types, escaping,
inaccessible or uncertain parents produce one bounded report with
`semantic_started: 0` and no uncaught pre-report exception.

The connected proof inventory includes separate non-noop production-guard
mutants for `MAX_PATH`, aggregate/deduplicated `MAX_PATHS`, each of the four
stream-specific `MAX_GIT_BYTES` guards, aggregate four-stream bytes and the
runtime-output ordering/type boundary. Every fault fixture otherwise has valid
Git/base/framing input so it reaches its intended production guard.

Alternative: infer coverage from aggregate success/failure cases. This is
rejected because disconnected or shared-gate fixtures do not prove individual
guard ownership.

### Published behavioral and authority floor

V6 reconstructs only from published sources and preserves exact 35→30
ownership, aggregate admission, strict four-stream selection, typed scheduler
output, full-only authority, source-safe CI, connected resolved-base guards and
protocol-artifact non-authority. Terminal unpublished v5 artifacts remain
unread and cannot satisfy any gate.

## Risks / Trade-offs

- [Authorization is treated as implementation closure] → Successor paths and
  executable changes remain absent until this card is published.
- [RED failure is masked] → Evidence requires non-zero capture status and a
  specific missing-symbol/module error.
- [Runtime output mutates before admission] → Exact target/parent fixtures and
  a connected ordering/type mutant must fail before semantic work.
- [Selector bounds share a disconnected oracle] → Every named guard receives
  its own otherwise-valid fixture and non-noop production mutant.
- [Ignored evidence is lost] → Lost mandatory RED evidence requires another
  clean lineage; later reproduction is insufficient.

## Migration Plan

1. Publish this docs-only authorization from exact investigation HEAD.
2. Create the sole v6 implementation from the authorization-publishing HEAD.
3. Retain and audit valid RED before production mutation.
4. Implement and review admission/proof contracts before final certification.

Rollback is omission of this unpublished authorization; published history is
not rewritten.

## Open Questions

None.
