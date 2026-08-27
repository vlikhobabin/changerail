## Context

Published affected v4 authorization ends at commit `3e85ce1de7e8b6f9bb60a04b924838e24064dd5b`.
Its unpublished implementation reached real RED before production changes, but
did not retain that raw run. Review cycle 2 therefore ended in terminal
`NO-GO`: a later exact-base reproduction can prove failure behavior, but cannot
prove the chronology of the original implementation.

## Goals / Non-Goals

**Goals:**

- Exhaust unpublished v4 without changing published history.
- Define one exact authorization and clean implementation path for v5.
- Make the pre-production RED payload, failure and ordering independently auditable.
- Preserve every published affected v4 behavioral and proof boundary.

**Non-Goals:**

- Reading, copying, cherry-picking or accepting v4 code or evidence.
- Creating v5 successor cards or executable artifacts in this decision.
- Running history, real full/affected, benchmark, live or certification checks.

## Decisions

### Clean lineage

The decision starts from the published v4 authorization HEAD. Unpublished v4
code, card, manifest, verdicts, logs and evidence are terminal forensic-only and
cannot satisfy future gates. The only conforming continuation is this decision,
docs-only v5 authorization, clean v5 implementation and certification.

The future authorization repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md","investigation_id":"rescue-affected-release-profile-red-evidence-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v5.md","successor_id":"implement-bounded-affected-release-profile-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on this rescue, the integration decision, scheduler v1 and
v4 authorization, and blocks only v5 implementation. The implementation uses
only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md","authorization_id":"authorize-bounded-affected-release-profile-v5"}
```

It depends on those four predecessors plus v5 authorization, blocks only
certification, starts from authorization-publishing HEAD and adds at most 499
production LOC.

### Retained RED before production mutation

V5 first creates only its card, OpenSpec and focused-test artifacts. Before any
production, CI or main-spec mutation, it invokes `bin/changerail-evidence
capture` with one command that first prints
`bin/changerail-review-verdict fingerprint --workspace .` and then runs the
focused test. The shell propagates the focused test's non-zero status; masking
the failure with a successful wrapper is invalid.

The retained entry must say `status: failed`, include a non-zero `exit_code`,
and point to raw output containing the pre-production `tree_sha`,
`diff_fingerprint` and a concrete missing production symbol/module error. A
later reproduction is diagnostic only and cannot replace this entry.

The fresh reviewer reads the retained evidence reference, verifies the saved
Git tree object exists, compares that tree against the authorization HEAD and
confirms that its only additions or changes are the allowed card, same-slug
OpenSpec and focused-test artifacts. Any production, CI or main-spec mutation,
missing tree object, successful capture status or nonspecific failure is
`NO-GO`.

### Published proof floor

V5 inherits the published v4 authorization rather than terminal code. It must
reconstruct exact 35→30 ownership, aggregate admission, strict bounded Git
selection, typed scheduler output, full-only authority, source-safe CI,
connected resolved-base guard mutants and protocol-artifact non-authority.

## Risks / Trade-offs

- [Ignored evidence is lost] -> Review and publish require the referenced raw
  entry in the same delivery workspace; losing it forces another clean lineage.
- [A failing test fails for the wrong reason] -> Require a specific missing
  production symbol/module and reviewer inspection of the raw output.
- [Fingerprint is printed after mutation] -> Reconstruct and diff the saved
  tree object against the exact authorization HEAD.
- [Rescue expands into implementation] -> Scope remains docs/OpenSpec only and
  successor paths must remain absent.

## Migration Plan

1. Publish this decision from the exact v4 authorization HEAD.
2. Publish a separate docs-only v5 authorization.
3. Start v5 from that authorization HEAD and capture valid RED before production.
4. Complete independent review, then certification, without using v4 artifacts.

Rollback is omission of the unpublished decision; published history is never
rewritten.

## Open Questions

None.
