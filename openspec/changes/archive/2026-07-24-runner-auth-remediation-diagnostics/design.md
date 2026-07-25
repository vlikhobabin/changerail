# Design: runner auth remediation diagnostics

## Context

`bin/changerail-delivery-runner` already records structured `Check` objects for
auth marker and stale symlink checks. The failure messages are safe but too
generic for first-time setup. The implementation can improve the existing
messages without schema changes.

## Goals / Non-Goals

**Goals:**
- Make missing auth and stale symlink messages actionable.
- Reference the canonical docs section or command examples.
- Preserve fail-closed status and existing check names.
- Keep status output free of credential contents.

**Non-Goals:**
- Do not add new status schema fields.
- Do not weaken auth checks or treat docs links as success.
- Do not inspect token contents or validate auth with the network.

## Decisions

- Keep `Check.name` values stable: `CODEX auth` and `CODEX_HOME symlinks`.
  This avoids downstream status schema churn and keeps existing smoke parsing
  intact.
- Change only `message` text to include a concise remediation hint. The hint
  names generic marker paths and docs, not real credentials.
- Stale symlink diagnostics keep listing the stale symlink paths already under
  `CODEX_HOME`, then append a remediation hint.

## Risks / Trade-offs

- [Risk] Longer messages could make aggregate queue output noisier.
  → Mitigation: keep the first clause short; compact plan diagnostics can still
  summarize by check name.
