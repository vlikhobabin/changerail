## Context

The retained runner-resume implementation reached deterministic review
preflight before semantic review. Preflight returned `investigation-required`
because the claimed payload added 562 production-counted lines in one built-in
classified source, `bin/changerail-delivery-runner`, and the card declared a
new runner/status protocol boundary without a published investigation
authorization.

The retained payload is useful investigation input, but it is not reviewed
evidence and must not be published. The already planned successor card
`support-runner-resume-after-investigation-required` remains the right story
boundary: retained identity, single-card resume and queue recovery are one
operator recovery workflow. Splitting queue recovery into a second delivery
would reduce the first payload size, but it would also publish a partial
retained-resume workflow that cannot satisfy the card's queue acceptance.

## Goals / Non-Goals

**Goals:**

- Publish a public-safe investigation decision for the stopped retained
  runner-resume payload.
- Bind the exact successor as
  `support-runner-resume-after-investigation-required`.
- Require a simplified successor implementation no larger than 500 added
  production-counted LOC.
- Preserve fail-closed retained-payload identity, authorization and queue
  recovery verification.
- State that the later authorization may permit the new runner/status protocol
  boundary only for this exact successor.

**Non-Goals:**

- No production runner, schema or smoke implementation changes in this
  investigation card.
- No authorization object is published by this change.
- No global complexity limit is raised.
- No checkpoint commit, stash, branch or prose assertion becomes review
  evidence.

## Decisions

1. Keep the exact successor card rather than creating a replacement card. The
   blocked work is oversized by 62 lines above the maximum authorization
   ceiling, not by a separate capability drift. Retained identity, single-card
   resume and queue recovery form one fail-closed recovery contract; publishing
   only part of that contract would leave downstream queue behavior unresolved.

2. Bound the successor through simplification, not weakened coverage. The
   implementation should reduce at least 63 production-counted lines by sharing
   retained-payload validation between single-card and queue resume paths,
   reusing existing manifest/review-preflight authorization helpers, avoiding
   duplicate status construction, and keeping plan recovery metadata compact.
   Smoke fixture setup may be shared, but required adversarial cases stay in
   the verification floor.

3. Use a later published authorization source for the complexity exception.
   This investigation card records the decision. A separate clean `4.done`
   authorization card must carry the machine-readable object with successor id
   `support-runner-resume-after-investigation-required`, production LOC ceiling
   `500` and `allow_new_authority_or_wire_protocol: true`. The successor card
   must also reference this published investigation in `Depends On`, and the
   investigation must continue to `Blocks` the successor, because deterministic
   preflight requires reciprocal relations.

4. Require the successor to run the full retained-resume floor before review:
   retained identity schema acceptance/rejection, single-card retained resume
   success, wrong card, wrong workspace, stale authorization, relation
   mismatch, over-ceiling, fingerprint drift, queue original resume, queue
   replacement recovery and duplicate recovery rejection.

## Risks / Trade-offs

- [Risk] LOC pressure could remove safety checks. Mitigation: the decision
  makes every fail-closed retained-resume case a successor verification target.
- [Risk] Allowing a protocol boundary could become a reusable waiver.
  Mitigation: the authorization must be exact-card, exact-path, clean at `HEAD`
  and tied to this investigation decision and successor only.
- [Risk] Keeping one successor card could still exceed 500 LOC. Mitigation: if
  the simplified implementation cannot meet the ceiling, this decision cannot
  authorize it; a replacement investigation/split card is required before
  another implementation attempt.

## Migration Plan

- Publish this decision-only card.
- Create and publish a separate authorization source card after this
  investigation is in `4.done`.
- Resume delivery of `support-runner-resume-after-investigation-required` only
  after the successor references the published authorization and the
  implementation is simplified below the 500 LOC ceiling.

## Open Questions

- none
