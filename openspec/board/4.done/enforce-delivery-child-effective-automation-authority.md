# Enforce delivery child effective automation authority

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Linked regression follow-up to
  `openspec/board/4.done/add-delivery-runner-child-equivalent-preflight.md`.
- A supervised nested delivery run proved that supervisor and single-card
  preflight passed, while the real Codex child still executed Git through a
  restricted command sandbox and stopped before planning or implementation.

## Summary
Make the unattended delivery runner's already-declared trusted automation
authority effective at the real Codex child command boundary. When an operator
explicitly supplies an isolated `CODEX_HOME` whose policy passes the existing
`never`/`danger-full-access` gate, the tracked ChangeRail Codex launcher must
start the child with the Codex invocation-level sandbox bypass.

The change must fail closed when the installed Codex CLI does not support that
mode, must not weaken the existing config/auth/publish-target checks and must
leave custom launchers plus generated default runtime homes unchanged.

## Review
- Risk tier: `critical`
- Review effort: `xhigh`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `yes`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

This card does not grant mutation authority. It makes the authority already
declared by an explicit operator-owned `CODEX_HOME` effective for the real
tracked Codex launcher. No new required runner/status fields are added.

## Depends On
- `openspec/board/4.done/add-delivery-runner-child-equivalent-preflight.md`

## Acceptance
- With the tracked ChangeRail Codex launcher and an explicit operator-owned
  `CODEX_HOME` whose policy passes the existing unattended authority gate, the
  real child command includes Codex's invocation-level approvals/sandbox
  bypass before `exec`.
- Preflight fails before child launch when that exact mode is required but the
  installed Codex CLI does not advertise support for it.
- Missing or insufficient `CODEX_HOME` policy, auth, clean-tree, upstream and
  publish-target checks remain fail-closed and are not replaced by the bypass.
- Default generated runtime homes and supported custom launchers preserve
  their existing command behavior; the runner does not silently apply a
  Codex-specific flag to them.
- Focused RED evidence fails on the missing real-child flag, then the matching
  GREEN test proves both the runner status argv and the launcher-observed argv.
- Durable docs and the delivery-runner spec explain the narrow explicit-home
  boundary and its critical-risk implications without adding required status
  schema fields or exposing credentials.
- Focused runner smoke, strict OpenSpec validation, whitespace checks,
  public-surface scan and the complete release baseline pass.

## Change Set
- `enforce-delivery-child-effective-automation-authority`

## Verify
- RED: retained `red-explicit-home-effective-authority` -> failed because
  tracked launcher argv was `/opt/changerail/bin/codex exec --json ...`
  without invocation-level authority.
- GREEN: retained `green-effective-authority-matrix` -> explicit trusted home
  propagates authority before `exec`, unsupported CLI blocks, generated home
  and custom launcher routes remain unchanged.
- GREEN: `python3 scripts/smoke-delivery-runner.py` -> delivery runner smoke
  passed.
- GREEN: `bin/openspec validate --all --strict` -> 24/24 before archive and
  23/23 after archive.
- GREEN: `git diff --check` plus explicit untracked scan -> no whitespace
  findings.
- GREEN: `python3 scripts/public-surface-scan.py` -> 1118 files scanned, 0
  findings.
- GREEN: `python3 scripts/run-release-baseline.py` -> 36/36 passed.
- Retained index:
  `.runtime/changerail/evidence/enforce-delivery-child-effective-automation-authority/index.json`.

## Archive
- `openspec/changes/archive/2026-08-21-enforce-delivery-child-effective-automation-authority/`

## Related
- `openspec/board/4.done/add-delivery-runner-child-equivalent-preflight.md`
- `bin/changerail-delivery-runner`
- `bin/codex`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `openspec/specs/changerail-delivery-runner/spec.md`

## Result
Delivered and awaiting independent review. The tracked Codex launcher now
propagates invocation-level authority only for an explicitly selected
operator-owned `CODEX_HOME` after existing trusted automation policy checks.
Preflight blocks unsupported Codex CLI versions, while generated runtime homes
and custom launchers keep their existing argv. No status schema field changed.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `enforce-delivery-child-effective-automation-authority`

### Why
The existing child-equivalent preflight proves the supervisor-visible
environment, but a nested Codex child can still apply an outer command sandbox
after the runner has accepted the tracked authority policy. The actual child
must receive an invocation-level authority mode that matches the operator's
explicit isolated automation home.

### Goal
Propagate already-validated explicit-home trusted automation authority to the
real tracked Codex child and fail closed when the installed CLI cannot enforce
it.

### Scope
- narrow tracked-launcher command construction for explicit `CODEX_HOME`;
- preflight capability check for the required Codex CLI mode;
- deterministic fake-Codex regression coverage for observed child argv;
- durable runner docs/specs;
- no status schema or custom-launcher protocol change.

### Acceptance
- The tracked launcher receives the invocation-level bypass only for explicit
  operator-owned trusted automation homes.
- Unsupported Codex CLI versions block before child launch.
- Custom launcher and generated-home behavior do not regress.
- Existing verification and public-safety floors pass.

### Depends On
- `openspec/board/4.done/add-delivery-runner-child-equivalent-preflight.md`

### Related
- `openspec/changes/enforce-delivery-child-effective-automation-authority/`

## Log
- 2026-08-21T13:36:25Z linked critical regression card created after a real
  nested child disproved effective sandbox parity while changing no tracked
  files.
- 2026-08-21T13:38:40Z apply-ready OpenSpec artifacts validated and card moved
  to `3.inprogress` for bounded implementation.
- 2026-08-21T14:03:35Z implementation, deterministic RED/GREEN coverage,
  durable docs/spec sync, focused smoke and 36-step release baseline passed;
  change archived and payload prepared for independent critical review.
- 2026-08-21T14:47:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
