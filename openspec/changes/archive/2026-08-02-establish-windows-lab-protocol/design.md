## Context

ChangeRail currently documents Linux-local release and wiring verification, but
native Windows support is still research-first. The `030` series has two
operator-managed Windows laptops available through ignored SSH inventory, and
future cards must probe symlink, junction, Git and runtime behavior without
touching real consumer repositories or exposing host identity in tracked files.

The protocol must be reusable by later cards while remaining public-safe in this
repository. Raw SSH commands, hostnames, usernames, private Windows paths and
session logs belong only under ignored `internal/` or `.runtime/changerail/`.

## Goals / Non-Goals

**Goals:**
- Define the Windows lab protocol in tracked compatibility documentation.
- Define the ignored inventory shape and generic host-id contract.
- Provide a local dry-run path for validating the harness without real hosts.
- Make timeout, cleanup, no-elevation and evidence-retention rules explicit.

**Non-Goals:**
- Implement native Windows runtime/bootstrap behavior.
- Register permanent CI workers or durable machine identities.
- Run destructive symlink/junction/runtime probes; those belong to `030-02`.

## Decisions

1. Use a single stdlib Python harness as the protocol entrypoint.
   - Path: `scripts/windows-lab-probe.py`.
   - Rationale: the existing repository already uses Python helpers for
     verification and smoke checks; stdlib keeps the protocol portable and
     avoids new runtime dependencies.
   - Alternative rejected: shell-only snippets in docs. They would be harder to
     validate, sanitize and re-run consistently across cards.

2. Keep raw connection data in ignored JSON inventory.
   - Default path: `internal/windows-lab-inventory.json`.
   - Required host fields: `id`, `ssh_command`, `disposable_root`.
   - Tracked output may mention only `windows-host-a` and `windows-host-b`.
   - Rationale: the operator can rotate hostnames, usernames, keys and root
     paths without changing public artifacts.

3. Treat live probe evidence as ignored runtime evidence.
   - The harness writes concise sanitized reports under
     `.runtime/changerail/windows-lab/`.
   - Raw command output remains ignored and is referenced only by path in cards,
     manifests or review verdicts.
   - Rationale: reviewers can audit current workspace evidence without copying
     machine-local data into tracked docs.

4. Use least-privilege SSH with bounded commands.
   - The protocol forbids elevation unless a future card records separate
     operator action.
   - Commands must use per-host timeouts and idempotent cleanup of the
     disposable probe directory.
   - Rationale: the lab is for research, not durable infrastructure management.

## Risks / Trade-offs

- [Risk] OpenSSH/PowerShell quoting differs by Windows setup. Mitigation: use
  encoded PowerShell commands for live probes and retain raw ignored output when
  a host fails.
- [Risk] Sanitization can hide useful debugging detail from tracked docs.
  Mitigation: keep concise outcome summaries in tracked docs and raw logs in
  ignored runtime evidence.
- [Risk] Disposable roots may be misconfigured to a real repository. Mitigation:
  the protocol requires roots outside consumer repositories, and the harness
  creates a per-run child directory instead of writing directly into the root.

## Migration Plan

1. Add the harness and protocol docs.
2. Run local dry-run validation with built-in sample hosts.
3. Use the same harness in `capture-windows-support-matrix` for live evidence.

## Open Questions

- Exact default/fallback runtime and wiring architecture remains out of scope
  until `030-03`.
