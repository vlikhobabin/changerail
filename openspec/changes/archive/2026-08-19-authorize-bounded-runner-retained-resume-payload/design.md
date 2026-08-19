## Context

The published investigation
`investigate-runner-retained-resume-payload-boundary` selected the existing
successor `support-runner-resume-after-investigation-required`, but only after
the retained implementation is simplified to at most 500 added
production-counted LOC. The successor already declares a published
authorization reference to
`openspec/board/4.done/authorize-bounded-runner-retained-resume-payload.md`,
but that authorization source is still a `2.todo` card and is not a clean
tracked `4.done` artifact.

This change supplies the missing source. It is intentionally smaller than the
runner implementation payload: it publishes one machine-readable authorization
object and verifies the existing deterministic preflight consumes that object
only for the exact reciprocal card chain.

## Goals / Non-Goals

**Goals:**

- Publish exactly one authorization object from the source card whose card id is
  `authorize-bounded-runner-retained-resume-payload`.
- Bind the object to investigation
  `investigate-runner-retained-resume-payload-boundary` and successor
  `support-runner-resume-after-investigation-required`.
- Preserve the production LOC ceiling at 500.
- Permit the new runner/status protocol boundary only because the completed
  investigation decision explicitly accepted that boundary for the exact
  retained-resume successor.
- Verify that deterministic preflight accepts the exact successor and rejects
  stale, missing or mismatched authorization links.

**Non-Goals:**

- Implement the retained runner-resume payload.
- Mark the successor card complete or publish its payload.
- Raise global ordinary review limits or introduce a reusable waiver mechanism.
- Broaden the JSON contract, credential authority or mutation authority.

## Decisions

1. The authorization source is the completed board card, not a separate schema
   file. Successor cards declare a compact JSON reference, and the published
   `4.done` source carries the full authorization payload.

2. The payload remains narrow and literal. It uses exact canonical board paths
   for `investigation_card` and `successor_card`, exact card ids for
   `investigation_id` and `successor_id`, integer ceiling `500`, and boolean
   protocol allowance `true`.

3. The `true` protocol allowance is scoped to the retained-resume runner/status
   boundary accepted by the investigation decision. It does not relax any
   credential, mutation, live-admission or global review gate.

4. Delivery should update only card/OpenSpec artifacts unless focused smoke
   coverage proves inadequate. If coverage is missing, the implementation may
   add minimal public-safe smoke coverage around existing preflight behavior,
   but it must not add production runner behavior.

5. The authorization cannot be considered consumable until publish moves the
   source card to `4.done`, the completed investigation is tracked in `4.done`
   and the successor reciprocally references this exact authorization source.

## Risks / Trade-offs

- [Overbroad exception] A prose waiver could be misread as a reusable policy
  change. Mitigation: keep the machine-readable object exact and require
  reciprocal-link verification.
- [Premature consumption] The successor might appear authorized before the
  source card is published. Mitigation: deterministic preflight must continue
  to require the clean tracked `4.done` authorization path.
- [Protocol-boundary ambiguity] Setting
  `allow_new_authority_or_wire_protocol` to true could be confused with a
  general authority waiver. Mitigation: bind it to the exact successor and the
  investigation's runner/status retained-resume boundary.
