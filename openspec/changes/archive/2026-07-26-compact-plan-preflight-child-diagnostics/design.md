## Context

`preflight-plan` already writes a schema-backed aggregate status and can launch
child single-card preflight checks. The UX gap is in the summary that reaches
the operator: a nested/truncated child JSON snippet is difficult to act on and
risks implying that raw child logs belong in aggregate status.

## Decisions

- Reuse existing status fields instead of changing
  `changerail-delivery-plan-status.schema.json`.
- Store compact child failure text in existing per-card `reason` and aggregate
  `checks[].message` fields.
- Keep full child evidence reachable through existing `cards[].run_status_path`.
- Human output for `preflight-plan` and non-JSON `status-plan` should list one
  compact line per failed child check.

## Public Safety

Diagnostics must be sanitized summaries. They may include card id, check name,
status and a short reason, but not child stdout/stderr, credential contents,
auth file contents or machine-specific absolute paths.
