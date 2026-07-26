## Context

Smoke coverage for delivery-plan commands already covers valid preflight, fail
closed semantic checks and live/resume behavior. The new UX should be covered
near that surface so regressions are caught by the existing release baseline.

## Decisions

- Keep focused coverage in `scripts/smoke-delivery-runner.py` instead of adding
  a separate runner.
- Assert behavior through CLI outputs and schema-validated status JSON.
- Check docs for durable phrases that encode launcher semantics and optional
  consumer `bin/codex` wording.
- Keep public-surface scan as a verification command, not as a generated tracked
  artifact.

## Public Safety

Smoke fixtures must use temporary repositories and generic card ids only.
Tracked docs must avoid private paths, secrets and machine-specific runtime
state.
