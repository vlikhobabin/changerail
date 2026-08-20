# Report Recovery-Aware Delivery Episodes

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
not-started

## Source
- Sanitized retrospective of a long-running supervised delivery with blocked
  attempts, manual recovery, independent review rescues and final publish.

## Problem
ChangeRail records each runner process, preflight and review artifact
independently. A card that blocks and resumes therefore has no canonical
delivery episode tying together the initial attempt, recovery attempts,
operator intervention, review cycles and publish result.

The current metrics report also counts preflight records as delivered runs,
associates a card's final review history with unrelated earlier preflights, and
does not ingest manual recovery runs. Terminal performance retains only the
last 50 command summaries and 100 timeline events, so a long delivery cannot be
reconstructed from structured records without reading raw agent logs and
inferring phases from artifact timestamps.

## Goal
Provide a privacy-safe, recovery-aware delivery episode and trustworthy
retrospective metrics without retaining prompts, command bodies or tool
payloads.

## Acceptance
- Every card execution has a stable `episode_id`; preflight, delivery,
  recovery, review, rescue and publish attempts have unique `attempt_id` and
  explicit parent/previous-attempt linkage.
- Each attempt records start/end time, terminal state, blocker class, phase
  transitions, active/wait/operator-wait durations, token usage, command/tool
  counts and bounded semantic outcome classes.
- Recovery launched through the supported workflow produces the same
  schema-versioned status and sanitized timing fields as the original child.
- Review history is append-only by cycle; the current canonical verdict may be
  replaced, but prior cycle result, finding ids and timestamps remain
  available to the episode report.
- `changerail-delivery-metrics` excludes preflight-only records from delivery
  success and first-pass-review rates by default, rolls attempts up by episode,
  and does not attach a later review to an unrelated preflight.
- Long runs preserve aggregate timing for all commands and MCP calls even when
  bounded detail samples are truncated; the record states the sampling limits.
- Operator intervention such as credential, license or external-state wait is
  represented by a value-free structured event and never captures the entered
  value or screen contents.
- Tests cover one-pass delivery, blocked/resumed delivery, multiple review
  rescues, abandoned recovery, preflight-only plans, truncated detail and
  secret-bearing synthetic tool output.

## Non-Goals
- Persisting raw prompts, shell commands, MCP arguments/results or screenshots
  in committable state.
- Replacing live progress heartbeats or the retained-payload authorization
  model.
- Inferring business acceptance from process telemetry.

## Related
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `schemas/changerail-delivery-run.schema.json`
- `expose-structured-live-delivery-progress.md`
- `resume-retained-payload-after-external-blocker.md`

## Verify
- Contract/schema smokes for attempt and episode records.
- Metrics fixtures proving preflight exclusion and recovery rollup.
- End-to-end fake runner with blocker, resume, no-go rescue, go and publish.

## Result
Not started.

## Next
Explore the episode identity, append-only review history and bounded telemetry
schema before implementation.

## Log
- 2026-08-20T17:30:00Z created from sanitized field-validation evidence.
