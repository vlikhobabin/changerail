## Context

Maintenance lifecycle reports already normalize deterministic scan findings and
baseline state. Maintainers still lack a stable quality view that combines
complete report snapshots, catalog coverage, triage annotations, proposal
decisions and optional future instruction-budget evidence. Delivery metrics are
not the right surface because their CSV columns are frozen for delivery-run
observability.

## Goals / Non-Goals

**Goals:**
- Add a separate maintenance quality rollup schema and CLI output surface.
- Read explicit lifecycle reports, state, triage annotations and optional
  proposal-decision records.
- Render human, JSON and stable CSV output with the same metric ids.
- Represent unavailable optional values as `unknown`.
- Keep proposal decisions as observations, not mutation authority.

**Non-Goals:**
- Do not change `bin/changerail-delivery-metrics` output or columns.
- Do not infer resolved counts from incomplete history.
- Do not invent instruction-budget thresholds before card `050` publishes its
  producer.
- Do not perform fixes, card writes or external mutations from rollup output.

## Decisions

1. Quality output has its own schema id.

   JSON output uses `changerail.maintenance-quality-rollup.v1`. This avoids
   expanding the lifecycle report contract with derived presentation metrics and
   lets the rollup use `unknown` values where lifecycle reports use concrete
   counts.

2. CSV is long-form and metric-id based.

   CSV rows use `metric,value,unit,status`, sorted by metric id. Alternative
   considered: a wide CSV with one column per metric. Long-form is more stable
   because new metrics add rows without changing existing columns.

3. Proposal decisions are explicit ignored runtime inputs.

   `changerail.maintenance-proposal-decision.v1` records live under
   `.runtime/changerail/maintenance/proposals/`. They capture proposal id,
   finding fingerprint, transformation class, decision, timestamp and safe
   evidence references. They are quality observations only.

4. Resolution requires ordered complete snapshots.

   A finding is resolved only when it appears in an earlier complete report and
   is absent from a later complete report. Incomplete or unordered history
   renders resolved metrics as `unknown`.

## Risks / Trade-offs

- [Risk] Missing optional inputs can make the rollup look sparse.
  Mitigation: text, JSON and CSV all expose explicit `unknown` status instead of
  reporting zero.
- [Risk] Proposal decisions could be mistaken for authorization.
  Mitigation: schema and docs state they are observations only; the command is
  read-only.
- [Risk] Board dedup metrics require scanning card text.
  Mitigation: the command only inspects exact `Maintenance Origin:
  <fingerprint>` markers and reports represented, missing and conflicting
  identities without mutating cards.

## Migration Plan

No migration is required. Existing lifecycle reports remain valid inputs.
Operators can start passing proposal decisions and triage annotations as
optional runtime evidence when available.

## Open Questions

- none
