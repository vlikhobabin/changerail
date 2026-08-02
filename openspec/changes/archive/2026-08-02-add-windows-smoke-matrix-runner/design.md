## Context

Cards `040-01` through `040-03` delivered focused deterministic coverage for
native Windows `.cmd` entrypoints, generated wiring, verifier/drift behavior and
Git safety. The architecture card still requires a higher-level implementation
matrix that can be run repeatedly, retain sanitized evidence and either cover
both Windows lab hosts or record an explicit blocker/caveat.

Existing reusable inputs:

- `scripts/smoke-windows-entrypoints.py` for `.cmd` wrapper contracts.
- `scripts/smoke-bootstrap-project.py` and `scripts/smoke-verify-project.py`
  for generated-copy ownership, stale copies, refresh and divergence fixtures.
- `scripts/smoke-windows-wiring-git-safety.py` for generated, symlink and
  junction Git status/add/index safety.
- `scripts/windows-lab-probe.py` and `scripts/windows-runtime-wiring-probe.py`
  for ignored inventory, generic host ids, disposable roots and sanitized live
  report shape.

## Goals / Non-Goals

**Goals:**

- Add `scripts/smoke-windows-matrix.py` as a single non-interactive runner for
  the deterministic local Windows support fixture matrix.
- Support optional live-host execution through ignored Windows lab inventory,
  using only `windows-host-a` and `windows-host-b` in tracked or summarized
  output.
- Write the aggregate smoke report under `.runtime/changerail/windows-smoke/`
  with sanitized command outcomes, host summaries and explicit blockers or
  caveats.
- Wire the platform-neutral matrix command into local release baseline and
  tracked CI inventory checks.

**Non-Goals:**

- Do not replace the focused smoke scripts; the matrix runner composes and
  audits them.
- Do not add real Windows CI credentials, inventory or host-specific workflow
  configuration.
- Do not claim live two-host coverage when the ignored inventory is missing or
  a host run fails.

## Decisions

1. Add an aggregate smoke script instead of extending every focused smoke.
   - Path: `scripts/smoke-windows-matrix.py`.
   - Rationale: the focused scripts remain useful for fast repair, while the
     matrix provides one acceptance-level command for the `040` series.
   - Alternative rejected: rely only on release baseline ordering; that would
     not produce a Windows-specific matrix report or live-host caveat.

2. Make local deterministic fixtures the default mode.
   - Default invocation: `python3 scripts/smoke-windows-matrix.py`.
   - The runner executes local commands with structured argv and records exit
     code, status and concise output summaries.
   - Rationale: Linux release baseline must exercise platform-neutral Windows
     contract tests without live host dependencies.

3. Keep live host mode explicit.
   - Optional flags: `--live`, `--inventory internal/windows-lab-inventory.json`
     and `--repeat`.
   - The runner reuses the ignored inventory conventions from the existing lab
     probes and refuses unignored inventory.
   - Rationale: host connection data and raw output are private runtime state.

4. Treat missing live coverage as evidence, not success, unless it is declared.
   - Default local mode records `live_status: not-run`.
   - Live mode records pass/fail per generic host id and exits non-zero on host
     failure.
   - Delivery may record an explicit caveat when hosts are unavailable, but the
     runner must not silently claim two-host coverage.

5. Preserve public-safe reporting.
   - The report schema id is `changerail.windows-smoke-matrix.v1`.
   - Raw command output paths remain ignored, and tracked cards/docs cite only
     report paths, command names, generic host ids and concise outcomes.
   - Sanitizers must reject private hostnames, SSH targets, credential-like
     values, raw Windows home paths and machine-local private roots.

## Risks / Trade-offs

- [Risk] The aggregate command becomes slow because it runs existing focused
  smokes. Mitigation: keep the runner simple, deterministic and only call the
  mandatory focused commands needed for matrix acceptance.
- [Risk] Live Windows hosts are unavailable during Linux delivery. Mitigation:
  keep live mode opt-in, record a caveat in the report/card and defer full host
  proof to the next `040-05` end-to-end card when necessary.
- [Risk] Reports leak private paths or host identities. Mitigation: write raw
  output only under ignored runtime state, use generic ids and gate tracked
  payload with public-surface scan.
- [Risk] The aggregate script masks focused smoke failures. Mitigation: each
  matrix item records the exact child command, exit code and status; any failed
  mandatory local item fails the matrix.
