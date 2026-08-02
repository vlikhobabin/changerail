## Context

The reusable probe from `add-windows-runtime-wiring-probe` supplies structured
host observations. This change turns live `030-02` runs into durable,
public-safe comparison evidence for `030-03`, while raw command output remains
under ignored runtime state.

## Goals / Non-Goals

**Goals:**
- Run the live runtime/wiring probe on `windows-host-a` and `windows-host-b`.
- Repeat the run after cleanup to confirm strategy conclusions are stable.
- Publish a sanitized comparison table in `docs/compatibility.md`.
- Update the board card with commands, outcomes, report paths and archive
  paths.

**Non-Goals:**
- Commit raw JSON reports or raw SSH output.
- Record hostnames, usernames, private Windows paths, SSH targets or
  credentials.
- Select the final ChangeRail Windows wiring/runtime architecture.

## Decisions

1. Store durable conclusions in compatibility notes.
   - Path: `docs/compatibility.md`.
   - Rationale: existing platform/tool observations live there, including the
     `030-01` support matrix.
   - Alternative rejected: commit generated runtime JSON; raw reports can carry
     machine-local paths and belong under `.runtime/`.

2. Cite both primary and repeatability evidence paths.
   - The first live run is the source for the tracked table.
   - The second run after cleanup must reach the same strategy conclusions or
     the report records the mismatch.
   - Rationale: the card acceptance explicitly requires repeatability after
     full cleanup.

3. Represent non-applicable cases explicitly.
   - Unavailable Developer Mode, missing Bash or elevated-only tokens are
     recorded as caveats instead of being hidden.
   - Rationale: architecture trade-offs need to know whether a strategy is
     portable or host-condition dependent.

## Risks / Trade-offs

- [Risk] A host may be temporarily unreachable. Mitigation: record a concrete
  sanitized blocker and do not claim a two-host conclusion.
- [Risk] Results may include machine-local paths in raw output. Mitigation:
  tracked docs cite only report paths under ignored `.runtime/` and generic
  host ids; public-surface scan gates the payload.
- [Risk] Repeatability can fail because cleanup failed. Mitigation: cleanup is
  an explicit check and failure blocks architecture conclusions.

## Migration Plan

1. Run dry-run validation for the harness.
2. Run primary live probe and retain ignored report path.
3. Run repeatability live probe after cleanup and compare strategy conclusions.
4. Update compatibility notes and the board card with sanitized outcomes.

## Open Questions

- Which strategy should become the implementation default is intentionally left
  for `030-03`.
