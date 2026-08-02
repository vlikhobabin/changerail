## Context

`add-native-windows-command-wrappers` adds tracked `.cmd` wrappers, but the
primary development and release baseline environment is Linux. This change adds
deterministic coverage that can inspect and exercise wrapper semantics without
requiring a live Windows host, while keeping the architecture requirement for
two-host live evidence explicit.

## Goals / Non-Goals

**Goals:**
- Cover argv, cwd, environment and exit-code behavior for the supported `.cmd`
  wrappers with deterministic fixtures.
- Include paths with spaces and non-ASCII characters in the fixture matrix.
- Add negative coverage for unsupported native defaults: extensionless POSIX
  launch and implicit Bash.
- Keep existing Linux/POSIX helper regression checks green.

**Non-Goals:**
- Replace live two-host Windows smoke evidence.
- Implement generated project-local wiring, drift checks or cleanup semantics.
- Depend on a Windows-only runtime in the primary Linux release baseline.

## Decisions

1. Add a focused local smoke instead of only extending broad release scripts.

   Rationale: a focused script gives delivery and review one cheap command that
   directly observes wrapper contract regressions. The release baseline can then
   call that smoke as one step.

2. Use deterministic fixtures for process semantics.

   Rationale: fixture wrappers can verify quoting, cwd, environment and exit
   code behavior in a reproducible way. Live Windows host evidence remains
   necessary before claiming full support, but fixture coverage prevents common
   regression classes from reaching that stage.

3. Record negative cases as contract checks.

   Rationale: direct extensionless POSIX launch and implicit Bash were rejected
   as native Windows defaults by the architecture card. Tests should make that
   boundary visible instead of silently allowing future code to rely on it.

## Risks / Trade-offs

- [Risk] Static or simulated checks can miss `cmd.exe` behavior. Mitigation:
  label them deterministic fixtures and keep live Windows smoke as explicit
  evidence or caveat.
- [Risk] Broad release baseline runtime increases. Mitigation: make focused
  fixture checks cheap and isolated from network or credentialed resources.
- [Risk] Tests become coupled to implementation formatting. Mitigation: assert
  observable wrapper behavior and supported surface, not incidental comments.
