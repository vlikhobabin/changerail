## Context

The runner change adds the executable Windows smoke matrix surface. This change
adds durable operator guidance so maintainers know how to run local fixtures,
when to use live host mode, how to retain sanitized reports and how to avoid
turning private SSH inventory into public ChangeRail docs.

Relevant existing docs:

- `docs/compatibility.md` already documents Windows lab protocol, support
  matrix, runtime/wiring results and the mandatory `040` test matrix.
- `docs/wiring-discovery.md` already describes generated-copy wiring,
  fallback proof and current Windows smoke expectations.
- `docs/release-discipline.md` documents local release baseline and focused
  smoke inventory.

## Goals / Non-Goals

**Goals:**

- Document local deterministic matrix execution and report interpretation.
- Document explicit live two-host execution, repeat-after-cleanup and caveat
  handling.
- Document future Windows CI integration as a path, not as committed private
  host infrastructure.
- Keep all examples public-safe with `/opt/changerail`, `/opt/example-project`,
  `windows-host-a` and `windows-host-b`.

**Non-Goals:**

- Do not add private SSH inventory, hostnames, usernames, credential paths or
  raw host output to tracked files.
- Do not claim that live Windows CI is already available.
- Do not change runner behavior after review; substantive runner fixes must go
  back through delivery and fresh review.

## Decisions

1. Put operational guidance near existing compatibility material.
   - Primary target: `docs/compatibility.md`.
   - Supporting target: `docs/release-discipline.md` if release-baseline
     command inventory wording needs the new matrix command.
   - Rationale: maintainers already consult these docs for Windows support
     claims and release gates.

2. Document exact commands but keep live inventory generic.
   - Local command: `python3 scripts/smoke-windows-matrix.py --json`.
   - Live command: `python3 scripts/smoke-windows-matrix.py --live --inventory
     internal/windows-lab-inventory.json --repeat --json`.
   - Rationale: the command is reproducible, while the inventory remains
     ignored operator state.

3. Treat caveats as first-class output.
   - Docs must explain that local matrix pass is not a two-host proof.
   - Live host blockers can be recorded as explicit caveats before support is
     claimed, but they do not silently satisfy host coverage.

4. Describe CI path without private infrastructure.
   - Linux CI runs the platform-neutral matrix.
   - Future Windows CI can provide an inventory through secure runner-local
     configuration and retain raw output under ignored artifacts.
   - Rationale: public repository content remains generic and reusable.

## Risks / Trade-offs

- [Risk] Documentation overstates native Windows support before live execution.
  Mitigation: explicitly distinguish local deterministic pass from live
  two-host coverage.
- [Risk] Examples encourage committing private inventory. Mitigation: every
  live command names `internal/windows-lab-inventory.json` and states that it is
  ignored.
- [Risk] Future CI wording implies credentials are available in GitHub Actions.
  Mitigation: describe the CI path as future secure runner configuration only.
