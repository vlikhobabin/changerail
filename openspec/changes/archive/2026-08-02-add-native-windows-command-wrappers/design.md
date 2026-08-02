## Context

`030-03` selected tracked `.cmd` entrypoints as the native Windows command
default. The repository already has POSIX wrappers in `bin/`, and Python-backed
helpers share the `bin/changerail-python` selector so Python diagnostics happen
before helper-specific imports. Native Windows support must add command
wrappers without changing the POSIX surface or requiring implicit Bash.

Affected helper surfaces for this card are:

- `bin/openspec`
- `bin/changerail-python`
- `bin/verify-project`
- `bin/changerail-review-verdict`
- `bin/changerail-evidence`
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`

## Goals / Non-Goals

**Goals:**
- Provide tracked `.cmd` wrappers for the supported helper surfaces listed by
  the card.
- Preserve argv, cwd, environment and exit code for native Windows launches.
- Keep Python-backed helpers routed through the shared runtime selector.
- Preserve existing POSIX wrappers unchanged except where compatibility tests
  require documentation or fixture updates.

**Non-Goals:**
- Implement generated project-local Windows wiring.
- Claim two-host live Windows support without live smoke evidence.
- Replace PowerShell diagnostics or make PowerShell the primary default.
- Add new third-party runtime dependencies.

## Decisions

1. Use one small `.cmd` wrapper per supported helper.

   Rationale: tracked per-helper entrypoints match Windows process launch
   conventions and keep future project-local generated copies simple. A single
   generic dispatcher would add quoting and dispatch complexity before there is
   evidence that it reduces maintenance cost.

2. Make `.cmd` wrappers sibling-aware.

   Rationale: wrappers in `bin/` can resolve their own directory via batch
   script metadata and invoke the sibling POSIX/Python-backed helper logic
   without assuming the caller's cwd. This preserves current operator habits
   where helpers are launched through repository-relative or absolute paths.

3. Route Python-backed wrappers through `changerail-python.cmd`.

   Rationale: `changerail-python` is the source of truth for supported Python
   selection and diagnostics. Each Python-backed helper should receive the same
   missing Python, unsupported Python and missing dependency behavior as POSIX
   launches.

4. Keep `openspec.cmd` pinned to the existing OpenSpec contract.

   Rationale: OpenSpec launch must use the same pinned version path as
   `bin/openspec`; native Windows launch must not fall back to extensionless
   POSIX execution or implicit Bash.

## Risks / Trade-offs

- [Risk] Batch quoting can accidentally split arguments with spaces or corrupt
  non-ASCII paths. Mitigation: implement with batch argument forwarding patterns
  covered by the follow-up deterministic fixture suite.
- [Risk] Linux-only validation cannot execute `.cmd` wrappers natively.
  Mitigation: keep this card's local verification focused on static contract
  checks and deterministic script tests; record live Windows smoke as explicit
  caveat when unavailable.
- [Risk] Divergent POSIX and Windows wrappers drift over time. Mitigation:
  keep wrappers thin and add release-baseline coverage in
  `test-native-windows-entrypoints`.

## Open Questions

- Whether `bin/bootstrap-project` becomes a supported native Windows helper
  entrypoint belongs to the wiring/backend card unless this card's implementation
  uncovers an unavoidable dependency.
