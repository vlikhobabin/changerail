## Context

The delivery runner already parses child JSONL for terminal outcomes, command
counts, timing and usage when available. That summary does not yet explain
output amplification: a command can be successful, failed, or runner-truncated
while producing enough output to dominate downstream token usage. Supervisors
need compact metadata in `status.json`; raw stdout/stderr and child JSONL
remain ignored evidence.

## Goals / Non-Goals

**Goals:**
- Record bounded byte counts for command stdout/stderr when child JSONL exposes
  enough information.
- Mark commands that exceed a documented threshold.
- Distinguish process failure, runner truncation and successful bounded result.
- Validate the fields through the delivery-run schema.

**Non-Goals:**
- Copy raw command output into `status.json`.
- Parse arbitrary free-text shell logs to reconstruct exact output.
- Change `DELIVERED`, `NO-GO` or `BLOCKED` terminal semantics based only on
  output size.
- Make historical runtime records invalid.

## Decisions

1. Store output metadata under `performance.commands[]` and top-level
   summaries, not under `logs`. `logs` remains references to ignored raw files.
2. Use byte counts and threshold flags, not token estimates, for command output.
   Token fields remain model-reported usage and may be unavailable.
3. Record classification only when supported by structured events. If JSONL
   lacks output bytes or truncation indicators, the fields are omitted or
   rendered unknown; the runner does not scrape arbitrary free text.
4. Schema additions are optional for compatibility. New fields are constrained
   by names, integer minimums and compact array limits in implementation.

## Risks / Trade-offs

- [Codex event shape changes] -> Parser records `unknown`/omits optional
  fields unless supported fields are present.
- [Status grows with command count] -> Implementation keeps existing top-N
  limits and avoids raw payload fields.
- [Output size is mistaken for failure] -> Specs keep terminal outcome
  semantics separate from amplification diagnostics.

## Migration Plan

Existing run records without output metadata remain valid. New runner versions
write metadata opportunistically when child JSONL provides enough structured
data.

## Open Questions

- Which Codex JSONL fields should be treated as authoritative for truncation
  once multiple CLI versions are observed?
- Should stderr and stdout thresholds share one value or have separate defaults?
