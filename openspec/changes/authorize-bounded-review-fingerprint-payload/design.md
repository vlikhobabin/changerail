## Context

The existing deterministic preflight contract already defines how a successor
card references a published investigation authorization. The missing piece for
the review-fingerprint replacement is the clean tracked authorization source:
the successor card points at
`openspec/board/4.done/authorize-bounded-review-fingerprint-payload.md`, but
that card is still a backlog story and has not yet been delivered.

This change is intentionally smaller than the implementation successor. It
publishes one machine-readable authorization object and proves that the existing
preflight accepts only the exact successor after reciprocal card relations are
valid.

## Goals / Non-Goals

**Goals:**

- Publish exactly one authorization object from the source card whose card id is
  `authorize-bounded-review-fingerprint-payload`.
- Bind the object to investigation
  `investigate-bounded-review-fingerprint-payload` and successor
  `deliver-bounded-review-fingerprint-optimization`.
- Preserve the production LOC ceiling at 500 and keep new authority or wire
  protocol disallowed.
- Verify that deterministic preflight accepts the exact successor and rejects
  stale, missing or mismatched authorization links.

**Non-Goals:**

- Implement the review-fingerprint optimization.
- Mark the investigation or successor card complete as part of planning.
- Raise global ordinary review limits or introduce a reusable waiver mechanism.
- Change the review preflight wire schema unless delivery discovers missing
  focused coverage that cannot be expressed with existing fields.

## Decisions

1. The authorization source is the completed board card, not a separate schema
   file. This follows the existing preflight contract: successors declare a
   compact JSON reference, and the published `4.done` source carries the full
   authorization payload.

2. The payload remains narrow and literal. It uses exact canonical board paths
   for `investigation_card` and `successor_card`, exact card ids for
   `investigation_id` and `successor_id`, integer ceiling `500`, and boolean
   protocol allowance `false`.

3. Delivery should update only card/OpenSpec artifacts unless focused smoke
   coverage proves inadequate. If coverage is missing, the implementation may
   add a minimal test case around existing preflight behavior, but it must not
   add a new authority surface or broaden the JSON contract.

4. The authorization cannot be considered consumable until publish moves the
   source card to `4.done` and the dependency investigation card is published.
   Before that, preflight must continue to fail closed for the successor.

## Risks / Trade-offs

- [Dependency not yet published] The current investigation card is not in
  `4.done`. Mitigation: the authorization change depends on the investigation
  and delivery must not claim the authorization is consumable before both
  source cards are published.
- [Overbroad exception] A prose waiver could be misread as a general policy
  change. Mitigation: keep the machine-readable object exact and require
  focused reciprocal-link verification.
- [Coverage gap] Existing smoke coverage may validate the generic contract but
  not this exact card chain. Mitigation: delivery must either point to focused
  passing preflight evidence for the exact chain or add minimal public-safe
  coverage.
