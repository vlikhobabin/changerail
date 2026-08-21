## Context

Investigation ограничила payload одним value-free event transport и status
projection, но protocol exception должен быть exact и tracked.

## Goals / Non-Goals

**Goals:** publish exact source with ceiling 500.

**Non-Goals:** implement progress or authorize raw telemetry.

## Decisions

- Protocol flag true applies only to progress/heartbeat/status boundary.
- Any successor/path mismatch or payload over 500 remains blocked.

## Risks / Trade-offs

- **Scope expands to raw telemetry.** Authorization remains invalid outside the
  investigated bounded fields.
