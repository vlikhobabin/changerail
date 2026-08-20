# Expose Structured Live Delivery Progress

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Supervised package delivery observation on a long-running single-card child.

## Summary
While a Codex child is running, the single-card status exposes only
`phase=delivery`, `result=RUNNING`, the process id and the original start time.
The aggregate plan mirrors only `state=running`. Operators cannot distinguish
active discovery, planning, implementation, verification or review without
reading the active raw JSONL log, which may contain credentials or private
runtime data and is intentionally not a supported status surface.

Add a bounded, secret-safe progress protocol so an orchestrator can observe a
long delivery without scraping child prose, commands, stdout or stderr.

## Acceptance
- A running single-card status contains a schema-versioned `progress` object
  with a bounded phase/stage enum, heartbeat timestamp and monotonic event
  counter.
- The child or runner updates progress at a documented interval and at major
  `ff -> do -> review -> publish` transitions without parsing free-form prose.
- Aggregate plan status mirrors the latest safe child progress and timestamp.
- Progress never contains prompts, shell commands, paths outside normalized
  card/workspace identifiers, environment values, response bodies or raw log
  excerpts.
- A stalled-child diagnostic uses heartbeat age and process state, but does not
  terminate or classify a live child solely because one interval was missed.
- Tests cover normal progress, stale heartbeat, child termination, resume and
  redaction/non-disclosure invariants.
- Existing terminal status, raw evidence retention and single-card/package
  compatibility remain unchanged.

## Change Set
- none yet

## Verify
- Contract/schema tests for single-card and aggregate status records.
- Runner integration fixture with deterministic progress events and stalled
  heartbeat.
- Secret-bearing synthetic child output proves progress remains value-free.

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`

## Result
not started

## Next
- triage

## Log
- 2026-08-20T09:54:00Z card created from sanitized supervised delivery
  evidence.
- 2026-08-20T17:30:00Z a later single-card delivery ran for 103 minutes and
  emitted 455 command executions, while its public status remained at the
  coarse delivery phase. The orchestrator could not distinguish source
  authoring, platform build, runtime proof, review wait, rescue or publish.
  Treat this as high priority before the next multi-card 1C package run.
