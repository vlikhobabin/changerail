## Why

The delivery runner currently summarizes command counts and timing, but
oversized command output can still make a run expensive without leaving compact
machine-readable evidence in `status.json`. Supervisors need bounded metadata
that distinguishes command failure, truncation and successful bounded results
without copying raw output.

## What Changes

- Extend delivery run status/schema behavior with bounded per-command
  output-byte metadata, stream/truncation indicators and threshold-exceeded
  flags.
- Distinguish command process failure, runner-observed truncation and successful
  bounded result when structured Codex JSONL provides enough fields.
- Keep status records compact by storing aggregate and top-N metadata only,
  while raw stdout/stderr remain ignored runtime evidence.
- Preserve existing terminal outcome semantics: output amplification metadata
  explains the run and remediation target without reclassifying delivery
  success or review outcomes by itself.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: structured runtime status gains bounded command
  output metadata and result/truncation classification.
- `changerail-contracts`: delivery-run schema documents the new bounded
  metadata fields and compactness constraints.

## Impact

- Affected files: `bin/changerail-delivery-runner`,
  `schemas/changerail-delivery-run.schema.json`,
  runner smoke coverage and OpenSpec artifacts.
- Consumer impact: supervisors can detect command-output amplification from
  status records without reading raw JSONL or stdout/stderr logs manually.
- Public-surface impact: status metadata is sanitized and bounded; raw command
  payloads remain ignored runtime evidence.
