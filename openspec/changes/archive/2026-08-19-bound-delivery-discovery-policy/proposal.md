## Why

Field validation showed that delivery children can amplify token usage by using
wide discovery commands against generated source and then treating truncated
output as evidence. ChangeRail needs an explicit agent-facing discovery
contract before runner-side telemetry can reliably guide remediation.

## What Changes

- Update delivery lifecycle guidance to require scoped discovery first:
  targeted paths, `rg -l`, counts, bounded excerpts and documented follow-up
  narrowing.
- Forbid treating truncated command output, including exit-130 output caused by
  runner or UI truncation, as proof that implementation is present or absent.
- Describe an explicit discovery budget/policy handoff that runner-launched
  children can receive without shell interception or language-specific rules.
- Preserve raw ignored runtime evidence; the bounded policy changes what agents
  consume and summarize, not retention of raw stdout/stderr.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-skill-surface`: delivery skill behavior gains bounded discovery
  policy and truncated-output evidence rules.
- `changerail-delivery-runner`: runner-launched child contract gains an
  optional public-safe discovery budget/policy handoff.

## Impact

- Affected files: `skills/changerail-deliver/SKILL.md`,
  `AGENTS.shared.md`, `bin/changerail-delivery-runner`, runner smoke coverage
  and OpenSpec artifacts.
- Consumer impact: wired ChangeRail delivery children receive clearer generic
  discovery behavior without requiring a shell sandbox or repository-language
  plugin.
- Public-surface impact: no private consumer logs, generated source snippets or
  local runtime records are tracked.
