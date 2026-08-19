## Why

The retained runner-resume payload stopped correctly before independent review:
deterministic preflight measured 562 added production-counted lines in
`bin/changerail-delivery-runner` and detected a new runner/status protocol
boundary without published investigation authorization. ChangeRail needs a
public-safe investigation decision that keeps the retained-payload safety model
but bounds the successor below the existing 500 production-LOC authorization
ceiling.

## What Changes

- Record the retained preflight stop as investigation input, not review evidence
  and not a publishable payload.
- Reproduce the public-safe source breakdown: one built-in classified production
  source, `bin/changerail-delivery-runner`, with 562 added production-counted
  lines.
- Keep the exact successor card as
  `support-runner-resume-after-investigation-required`, but require a simplified
  implementation no larger than 500 added production-counted LOC.
- Preserve the required retained-resume verification floor: retained identity
  schema acceptance/rejection, single-card retained resume success, wrong
  card/workspace, stale authorization, relation mismatch, over-ceiling,
  fingerprint drift, queue original resume, queue replacement recovery and
  duplicate recovery rejection.
- Do not publish an authorization object, change production runner behavior,
  treat checkpoint commits as review evidence or raise
  `MAX_AUTHORIZED_PRODUCTION_LOC_LIMIT`.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: deterministic review preflight and retained-payload
  recovery documentation have one tracked investigation decision for the runner
  resume successor, including the exact successor boundary, LOC ceiling and
  verification floor.

## Impact

- Affected tracked files: this board card and
  `openspec/changes/decide-runner-retained-resume-payload-boundary/`.
- Expected payload is board/OpenSpec documentation only; production runner code,
  schemas and smoke tests remain unchanged by this investigation card.
- Consumer impact is procedural: the retained-resume implementation must be
  simplified and separately authorized before the critical runner/status
  protocol payload can reach semantic review.
