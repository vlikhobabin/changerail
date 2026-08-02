## Context

`add-windows-generated-wiring-backend` introduces generated-copy creation and
ownership metadata. This dependent change makes that backend durable: generated
copies must be refreshable, stale copies must fail verification, partial
bootstrap failure must not remove project-owned work, and symlink/junction modes
must stay explicit bounded fallbacks.

The existing verifier currently treats required surfaces as symlink-и. The new
logic must accept generated-owned surfaces when project policy says they are
generated, and fail closed when content drift, project-owned divergence or
missing fallback proof appears.

## Goals / Non-Goals

**Goals:**
- Add refresh/upgrade behavior that updates only generated-owned artifacts.
- Detect stale generated copies and project-owned divergence through
  `verify-project` or the drift gate.
- Roll back only artifacts created by the current failed run.
- Gate Windows symlink fallback on explicit opt-in plus positive
  privilege/Developer Mode proof.
- Gate Windows junction fallback on explicit opt-in plus link-aware cleanup and
  Git-safety evidence.
- Keep POSIX symlink wiring compatible.

**Non-Goals:**
- Promote symlink or junction mode to a Windows default.
- Prove live two-host Windows support; later `040` cards own automated smoke
  and end-to-end proof.
- Add credentials, host identities or runtime reports to tracked files.

## Decisions

1. Make generated ownership the authority for refresh.

   Rationale: source digests alone cannot determine whether a consumer file is
   safe to overwrite. Refresh updates only entries explicitly marked
   generated-owned and refuses entries marked or detected as project-owned.

2. Treat stale generated copies as blocking verification findings.

   Rationale: a stale generated command, skill or helper surface can change
   agent behavior. Verification must identify the artifact and remediation
   path instead of silently refreshing during a read-only check.

3. Use a per-run created-artifact ledger for rollback.

   Rationale: partial failure cleanup must be bounded to artifacts created by
   the current run. Existing project-owned files and preexisting generated
   surfaces are left intact unless an explicit refresh operation owns them.

4. Require schema-valid, evidence-bearing fallback proof before reporting
   success.

   Rationale: `030-03` showed elevated symlink success but did not prove
   least-privilege symlink behavior. Symlink fallback therefore requires
   Developer Mode or privilege proof, while junction fallback requires Git
   status, dry-run add and index safety checks plus link-aware cleanup. The
   report must include source metadata, check details and concrete retained
   evidence; passed status names alone are rejected.

## Risks / Trade-offs

- [Risk] Project-owned divergence can block refresh for a legitimate local
  customization. Mitigation: report it as project-owned with a remediation path
  rather than overwriting it.
- [Risk] Junction cleanup can recurse into ChangeRail source if implemented as
  normal directory removal. Mitigation: classify link paths before cleanup and
  unlink the junction itself.
- [Risk] Fallback probes can be flaky across Windows host policy. Mitigation:
  report unavailable proof as fail-closed fallback evidence, not as generated
  default failure.
- [Risk] Smoke coverage on Linux cannot prove Windows privileges. Mitigation:
  deterministic fixtures cover policy and classification; later live-host cards
  own host execution.

## Open Questions

- If existing Windows consumers predate the manifest, a future adoption command
  may need an explicit import flow. This card can require project policy for new
  generated consumers and leave legacy import as a follow-up if no such surface
  exists yet.
