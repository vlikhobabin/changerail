## Context

Codex has two distinct configuration roles: user-level mutable state under
`CODEX_HOME` and trusted project policy under `<workspace>/.codex/config.toml`.
The runner currently aliases both roles by setting default `CODEX_HOME` to the
tracked project directory. A real `codex exec` reproduction showed that startup
can append `[projects."<absolute-workspace>"]` to that file; passing the same
trust value through `-c` does not suppress persistence.

Consumer repositories already ignore `.runtime/` and auth markers under
`.codex/`. The runner must preserve project MCP/policy loading, unattended
authority checks, workspace-local skill diagnostics and explicit external
`CODEX_HOME` support without reading or copying credentials.

## Goals / Non-Goals

**Goals:**

- Keep tracked project config byte-stable during default child startup.
- Give Codex an exact absolute trust binding through ignored mutable state so
  the project layer is loaded.
- Reuse ignored project auth markers by reference and retain supported auth
  environment variables.
- Keep preflight fail-closed and deterministic before child launch.
- Preserve explicit operator `CODEX_HOME` as an unmanaged compatibility path.

**Non-Goals:**

- Changing Codex's trust persistence behavior.
- Storing, parsing, copying or rotating credential contents.
- Migrating consumer project policy into generated runtime config.
- Changing `bin/codex` interactive launcher semantics in this bounded change.
- Introducing a new wire schema or tracked machine-local state.

## Decisions

### Generate a dedicated ignored default home

Absent an explicit environment override, the runner uses
`<workspace>/.runtime/changerail/codex-home`. Before preflight it creates the
directory with mode `0700` and atomically reconciles a mode `0600`
`config.toml` containing only an exact absolute workspace trust table and a
generated-file warning.

Every component below the resolved workspace root in this runner-owned
directory chain must be an ordinary directory. A preexisting symlink is
rejected before chmod or reconciliation so it cannot redirect generated files
into the tracked project layer.

This location is stable across single-card and plan runs, remains outside the
review payload, and is already covered by the consumer `.runtime/` ignore
contract. A per-run home was rejected because it needlessly duplicates auth
links and mutable Codex cache/state. Keeping `<workspace>/.codex` as default was
rejected because CLI trust overrides did not prevent the tracked mutation.

### Keep project policy as the authority source

For the generated default home, preflight reads unattended
`approval_policy`/`sandbox_mode` from `<workspace>/.codex/config.toml`. The
runtime user config supplies trust only; after trust resolution, Codex loads the
project config as the higher-precedence project layer.

For an explicit operator `CODEX_HOME`, existing behavior is preserved:
preflight reads `<CODEX_HOME>/config.toml`, checks auth there and does not create
or rewrite the directory. This keeps existing centralized homes compatible and
makes their mutability an explicit operator choice.

### Link auth markers without copying them

If no supported auth environment variable is present, preparation selects the
first existing project `.codex/auth.json` or `.codex/auth.toml` marker and
creates a symlink with the same name in the generated runtime home. It never
opens the marker or copies contents. Missing auth remains a preflight failure.
Runner-owned stale or conflicting links are reconciled only inside the ignored
generated home.

### Check both configuration layers

Default preflight checks stale symlinks in both the generated home and project
`.codex/`, retaining diagnostics for project skill links. Diagnostics identify
the layer and never include credential contents. The clean-tree check happens
after runtime preparation, proving generated state is actually ignored; a
consumer with incorrect ignore wiring therefore fails closed.

### Regression models the real persistence side effect

The fake child appends an absolute trust table to its received
`CODEX_HOME/config.toml`, matching the reproduced Codex startup behavior. The
smoke records the tracked project config bytes before launch and asserts they
are identical afterward, the generated home is private and ignored, and the
workspace has no new tracked diff.

## Risks / Trade-offs

- [Consumer does not ignore `.runtime/`] → Preparation makes the tree dirty and
  existing clean-workspace preflight blocks before launch.
- [Auth marker target becomes stale] → Combined symlink diagnostics fail closed
  and point to documented remediation.
- [Generated config overwrites user customization] → Only the dedicated
  runner-owned default home is reconciled; explicit `CODEX_HOME` is never
  rewritten.
- [Project policy is not loaded] → Exact absolute trust plus regression checks
  cover the project boundary; preflight independently parses project authority.
- [Absolute paths appear in runtime state] → They remain ignored and are never
  added to tracked docs, specs, manifests or evidence claims.

## Migration Plan

1. Publish the runner, smoke and documentation change.
2. Existing consumers keep tracked `.codex/config.toml` and ignored
   `.codex/auth.*` unchanged.
3. The next preflight lazily creates the ignored runtime home and auth link.
4. Explicit `CODEX_HOME` invocations continue with legacy semantics.
5. Rollback is code-only; generated ignored state can remain harmlessly on
   disk and contains no copied credentials.

## Open Questions

- none
