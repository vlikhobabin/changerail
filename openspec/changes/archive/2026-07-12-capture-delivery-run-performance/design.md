## Context

`bin/changerail-delivery-runner` streams child stdout into `stdout.jsonl` and
updates `status.json` at phase boundaries. The raw child events may contain
command lifecycle items, usage objects and terminal outcome events, but the
runner currently does not attach observed timestamps or aggregate command
durations while the stream is live.

## Goals / Non-Goals

**Goals:**
- Add runner-observed timestamps for JSONL events handled during streaming.
- Aggregate command lifecycle events into command counts, durations and slowest
  command summaries.
- Add available event counts, agent message counts, file-change counts,
  terminal outcome timing and review/publish latency to status performance.

**Non-Goals:**
- Do not parse arbitrary prose from stdout/stderr.
- Do not change review-gated fallback outcome rules.
- Do not require Codex to emit one fixed JSONL schema for all future versions.

## Decisions

- Capture timing at the runner boundary with `time.monotonic()` for durations
  and UTC timestamps for timeline entries. This avoids depending on child event
  clocks.
- Treat command lifecycle extraction as best-effort. Recognized start/complete
  events produce durations; unmatched or unknown events still count in the
  timeline but do not create fake durations.
- Keep full raw stdout/stderr as ignored evidence and write only compact
  summaries in `status.json`. This protects public surface and keeps status
  bounded.
- Read review-cycle history and current git status after child exit for summary
  fields that cannot be known during streaming.

## Risks / Trade-offs

- [Risk] Codex JSONL event names can change.
  Mitigation: parser accepts several common command lifecycle shapes and treats
  unknown shapes as generic events.
- [Risk] Long runs can produce large timelines.
  Mitigation: status keeps bounded summary fields and slow-command samples.
- [Risk] Duration tests can be flaky if they assert exact values.
  Mitigation: smoke tests assert measurable non-negative durations and command
  counts, not exact timing.
