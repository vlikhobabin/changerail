## Why

After runner metadata exists, operators still need a concise human-facing view
that identifies which commands caused amplification and what to do next.
Metrics and documentation also need to explain output size alongside cached and
uncached token usage, including runs where token usage is unavailable.

## What Changes

- Add operator-facing summaries that list top oversized commands in sanitized,
  bounded form with remediation guidance.
- Extend metrics/observability reporting to include command output thresholds,
  top oversized commands and token-usage availability semantics.
- Add synthetic smoke coverage that emits oversized command output and proves
  bounded status size, correct byte accounting and no raw payload copy.
- Document the relationship between output size, cached/uncached token metrics
  and `unknown` token fields.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-observability`: metrics and docs expose oversized output
  summaries and token-availability semantics.
- `changerail-delivery-runner`: operator-facing runner summary reports top
  oversized commands with remediation.

## Impact

- Affected files: `bin/changerail-delivery-runner`,
  `bin/changerail-delivery-metrics`, `scripts/smoke-delivery-runner.py`,
  delivery observability docs and OpenSpec artifacts.
- Consumer impact: operators get actionable amplification diagnostics without
  disclosing source content, secrets or raw generated output.
- Public-surface impact: synthetic smoke fixtures use generic generated data and
  retain only bounded summaries in tracked artifacts.
