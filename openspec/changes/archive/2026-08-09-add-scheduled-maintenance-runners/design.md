## Context

The maintenance CLI now produces deterministic scan and lifecycle report output.
Recurring use needs a scheduler-neutral wrapper that records status, enforces
timeouts and prevents overlapping runs, while keeping scheduler examples
least-privilege and public-safe.

The runner is not a delivery runner clone. It owns maintenance audit execution
only: scan mode is deterministic and must work without Codex auth; optional
triage mode may launch an agent only after scan/report data exists and explicit
budget/time bounds are provided.

## Goals / Non-Goals

**Goals:**
- Add POSIX and native Windows maintenance runner entrypoints.
- Publish `changerail.maintenance-run.v1` status under ignored runtime state.
- Keep scan mode read-only and independent of Codex auth.
- Add atomic non-overlap lock, timeout and budget diagnostics.
- Validate child output fail-closed for optional triage.
- Add public GitHub Actions, systemd, Codex scheduled task and CI separation
  examples.

**Non-Goals:**
- Do not implement issue tracker, PR, comment or push integrations.
- Do not make maintenance scans mandatory for delivery or bootstrap.
- Do not guarantee exact scheduler timing or exactly-once execution.
- Do not add provider-specific secret handling beyond least-privilege examples.

## Decisions

1. The runner status lives under
   `.runtime/changerail/maintenance/runs/<run-id>/status.json`. Alternative:
   reuse delivery-run status. Rejected because maintenance has different modes,
   artifacts and auth requirements.
2. Scan mode calls the deterministic maintenance CLI directly and never needs
   Codex auth. Alternative: always launch an agent. Rejected because scheduled
   read-only scans must run in low-privilege environments.
3. Triage mode consumes a completed scan/report and validates schema-bound
   child output before accepting annotations/previews. Alternative: scrape
   natural-language agent output. Rejected because unattended control flow must
   use machine-readable contracts.
4. The lock is an atomic runtime file/directory below the run root and blocks
   concurrent runs in one workspace. Alternative: rely on scheduler-specific
   concurrency controls. Rejected because every scheduler has different
   guarantees.
5. Examples remain below `examples/maintenance/` and use generic paths only.
   GitHub Actions gets `contents: read`; write-capable jobs are documented as
   separate explicit flows.

## Risks / Trade-offs

- [Risk] A stale lock can block later runs. -> Mitigation: status records lock
  diagnostics and remediation; automatic deletion is out of scope.
- [Risk] Scheduled triage can spend unbounded tokens or time. -> Mitigation:
  triage requires explicit timeout and agent budget fields in status.
- [Risk] Scheduler examples may be copied into write-capable contexts. ->
  Mitigation: examples separate read-only analysis from any write/API job and
  document default-branch/at-least-once scheduler behavior.

## Migration Plan

Add the runner, schema, fixtures and examples without changing
`bin/changerail-maintenance`. Existing manual scan/report users are unaffected.
Schedulers can adopt the new runner by invoking scan mode from the repository
root.

Rollback removes the runner/examples/status schema while leaving deterministic
maintenance CLI contracts intact.

## Open Questions

- none
