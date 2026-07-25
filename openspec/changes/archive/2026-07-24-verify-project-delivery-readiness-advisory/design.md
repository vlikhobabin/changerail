# Design: verify-project delivery readiness advisory

## Context

`verify-project` is a red/green gate for consumer wiring and public-safety
policy. Missing runner auth is not always a project verification failure:
public CI, fresh templates and non-runner consumers can be valid without local
credentials. The verifier should still tell an operator whether delivery runner
auth readiness is present.

## Goals / Non-Goals

**Goals:**
- Add a non-fatal advisory to text and JSON verification output.
- Detect project-local `.codex/auth.json` or `.codex/auth.toml` marker and
  supported auth environment variables.
- Keep existing pass/fail summary based only on mandatory checks.
- Provide a clear remediation pointer.

**Non-Goals:**
- Do not read credential contents.
- Do not make auth required for `verify-project`.
- Do not validate network connectivity or token freshness.

## Decisions

- Reuse a separate `Advisory` dataclass instead of overloading `Check.ok`.
  Checks remain fail-closed for mandatory wiring; advisories report readiness
  state without changing exit code.
- JSON output gets an `advisories` array and advisory summary. This is additive
  and does not remove existing fields.
- Text output uses `INFO` or `WARN` prefixes so operators can distinguish
  non-fatal readiness from failures.

## Risks / Trade-offs

- [Risk] Consumers may parse text output and treat any `WARN` as failure.
  → Mitigation: exit code and JSON `summary.status` remain tied to mandatory
  checks only.
