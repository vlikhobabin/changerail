## Context

`bin/changerail-delivery-runner` already writes ignored
`changerail.delivery-run.v1` status records for single-card delivery runs.
When a delivery child stops with `terminal_reason: investigation_required`, the
runner can preserve a dirty working tree for operator investigation, but the
status record does not yet bind that dirty tree to a verifiable payload identity.

The recovery contract must stay public-safe because ChangeRail is public by
default. The status may reference ignored runtime evidence, but tracked schemas
and OpenSpec artifacts must not require raw source payloads or raw child logs.

## Goals / Non-Goals

**Goals:**

- Record retained-payload identity only for the exact
  `investigation_required` safety stop.
- Make the identity schema-backed and sufficient for a later resume check to
  detect wrong card, wrong workspace, stale status and fingerprint drift.
- Reuse the canonical review fingerprint semantics already used by review
  verdict freshness.
- Keep raw source, raw logs and ignored runtime evidence out of tracked
  artifacts.

**Non-Goals:**

- No resume behavior is implemented by this change.
- No clean-tree requirement is relaxed for ordinary `run`, `run-plan` or remote
  preflight resume.
- No WIP commit, stash, branch name or human assertion is accepted as proof.

## Decisions

1. Add a bounded `retained_payload` object to `changerail.delivery-run.v1`.
   The object uses `schema: changerail.retained-payload-identity.v1` so future
   consumers can validate it without parsing prose. Alternative considered:
   encode the values in the `terminal_reason` message. That would not be
   schema-valid and would be brittle for queue resume.

2. Capture the same fingerprint tuple that review freshness uses:
   workspace root, card path/id, `HEAD` commit, reviewed tree SHA and
   `diff_fingerprint`. The implementation should call the existing canonical
   fingerprint helper rather than adding a second hashing algorithm.
   Alternative considered: record only `git status --porcelain`. That detects
   dirtiness but does not prove payload identity.

3. Treat identity capture failure as a separate fail-closed status detail. If
   the runner cannot compute the retained-payload fingerprint, it should still
   preserve the original `BLOCKED` result but record a stable diagnostic such as
   `retained_payload_identity_unavailable`. A later resume must reject that
   status until a valid identity exists.

4. Store only bounded metadata. `retained_payload` may include ignored runtime
   paths such as the source run status path, but it must not include raw source
   snippets, raw child stdout/stderr, secrets or customer data.

## Risks / Trade-offs

- [Risk] The new object duplicates fields already present elsewhere in the
  status record. Mitigation: duplicate only identity-critical values so resume
  can validate the exact prior stop without following mutable logs.
- [Risk] Fingerprint computation may be expensive on large repositories.
  Mitigation: use the existing optimized canonical fingerprint implementation
  and keep this path limited to safety stops.
- [Risk] Status records are ignored runtime files and can be edited manually.
  Mitigation: resume must verify the recorded identity against the current
  workspace before trusting it.

## Migration Plan

- Extend `schemas/changerail-delivery-run.schema.json` with the optional
  `retained_payload` object.
- Update `bin/changerail-delivery-runner` to populate it when the terminal
  reason is `investigation_required`.
- Add focused synthetic coverage for a blocked retained-payload status.

## Open Questions

- none
