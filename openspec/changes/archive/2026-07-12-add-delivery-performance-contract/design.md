## Context

`changerail.delivery-run.v1` already defines the base status record and requires
`usage.available`. The schema and docs do not describe performance breakdowns,
so runner and metrics changes would otherwise invent their own field names.
Runtime logs remain ignored evidence; the public contract should describe only
structured metadata safe to expose in status records and documentation.

## Goals / Non-Goals

**Goals:**
- Add optional schema-backed `performance` fields for timing and counts.
- Extend `usage` with optional cached, uncached and reasoning token breakdowns.
- Document which fields are mandatory, best-effort or rendered as `unknown`.

**Non-Goals:**
- Do not require every provider or child JSONL shape to expose every timing
  field.
- Do not publish raw child stdout/stderr as tracked evidence.
- Do not change terminal outcome semantics.

## Decisions

- Keep the base `timestamps.started_at`, `result`, `command` and `usage` fields
  required. Performance details are optional because older runtime records and
  limited child streams must remain readable.
- Add a top-level `performance` object instead of spreading fields across the
  root status record. This keeps the contract discoverable and avoids changing
  existing root-level consumers.
- Represent missing optional timing data by omission in JSON and by `unknown`
  in metrics/docs output. This preserves schema validity without guessing.
- Allow compact timeline entries and aggregated summaries. A full event stream
  can stay in ignored `stdout.jsonl`, while `status.json` carries enough
  machine-readable data for common diagnostics.

## Risks / Trade-offs

- [Risk] Optional fields may be interpreted as complete timing coverage.
  Mitigation: docs and specs explicitly label these fields best-effort.
- [Risk] Schema additions can reject future runner data if they are too narrow.
  Mitigation: define typed nested objects for known summaries and keep event
  names as strings, not closed enums.
- [Risk] Token usage providers use different terminology.
  Mitigation: keep canonical ChangeRail field names and allow absent breakdowns.
