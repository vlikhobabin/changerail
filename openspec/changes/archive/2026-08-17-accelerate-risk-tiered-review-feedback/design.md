## Context

Manifest validation, scope comparison and verdict fingerprinting already exist,
but the review skill asks an LLM reviewer to orchestrate them. Machine-detectable
failures therefore arrive as costly review findings. The existing default of
five same-card rescues is not risk-aware and does not distinguish planning,
implementation and live-admission reviews.

## Goals / Non-Goals

**Goals:**

- Reuse the existing manifest and review-verdict helpers.
- Emit one stable machine result before any LLM payload review.
- Normalize only safe manifest metadata and operation mismatches when the path
  set is unchanged; never absorb extra or missing paths.
- Make review effort and counters explicit.
- Stop rescue growth before a patch staircase creates a new subsystem.

**Non-Goals:**

- Launch or manage an LLM from Python.
- Infer semantic risk from arbitrary source text.
- Replace independent semantic review for ordinary or critical payloads.
- Introduce a durable tracked runtime ledger.

## Decisions

1. `bin/changerail-review-verdict preflight` is the public entrypoint.

   The already-wired review helper delegates to a small module that reuses
   `changerail_delivery_manifest.py` and verdict fingerprint logic. Consumer
   projects need no new launcher or wiring surface.

2. Normalization is deliberately narrow.

   With `--normalize`, preflight refreshes same-card metadata, archived-change
   state and operation details only when expected and actual comparable path
   sets are identical. Missing or extra paths remain blockers and are never
   copied into the manifest.

3. Risk is declared, not guessed.

   Cards use `## Review` fields. Missing risk defaults to `ordinary` for legacy
   cards. `deterministic` routes to machine-only review and is rejected when
   production code is added. `ordinary` recommends `high`; `critical` recommends
   `xhigh`. Credential/mutation/live/final boundaries must be declared critical
   by planning/delivery policy.

4. Complexity is a typed stop.

   Preflight counts added production lines in scoped code paths. More than 300,
   an explicitly declared new authority/wire protocol, or a repeated defect
   class yields `investigation-required`; it does not consume another
   implementation review cycle.

5. Payload review and final certification are different milestones.

   Each publish gets one risk-appropriate payload review. Focused re-review may
   reuse unchanged full-suite evidence bound to the same tree hash. Only one
   explicitly declared clean-HEAD LLM audit is permitted at a milestone, and the
   full suite is rerun immediately before live admission or final publication.

6. Phase counters remain optional and backward compatible.

   Review history gains `phase_counters` for planning, delivery fix,
   implementation review and live admission. Existing `review_cycle` continues
   to mean semantic implementation payload review only.

## Risks / Trade-offs

- Explicit risk can be understated. The review/delivery contract requires
  critical classification for credential, mutation, live-admission and final
  certification boundaries, and reviewers treat understatement as a blocker.
- Machine-only review cannot assess semantic prose quality. It is allowed only
  for explicitly deterministic/process payloads with no added production code.
- A 300-line threshold is intentionally coarse. It is an investigation trigger,
  not a prohibition; a simplified/replanned change may justify the resulting
  design explicitly.

## Migration Plan

1. Add schema, preflight implementation and focused smoke.
2. Extend optional history counters and contract smoke.
3. Update lifecycle sources and templates.
4. Sync main specs, archive the change and hand the dirty payload to one fresh
   independent reviewer.

## Open Questions

- none
