## Context

Consumer projects are separate repositories. They should expose OPSX skills,
commands and helper wrappers through symlink-и or documented generated copies,
while keeping project-specific `AGENTS.md`, `.mcp.json`,
`.codex/config.toml` and OpenSpec artifacts local.

## Decision

Implement `bin/verify-project` as a Python-backed executable gate. It prints
one check per line and exits `0` only when every required check passes. It
accepts:

```text
bin/verify-project <path> [--opsx-root /opt/opsx] [--aggregator-root <path>]
```

The default OPSX root resolves from the wrapper location, not from the current
working directory.

## Checks

- Required symlink-и:
  - `.claude/skills`
  - `.claude/commands/opsx`
  - `.codex/skills/opsx-*`
  - `.codex/skills/openspec-*`
  - `bin/openspec`
  - `bin/opsx-review-verdict`
- Symlink resolution must land inside OPSX root directly, or inside an
  explicitly provided aggregator that itself resolves to OPSX for OPSX-owned
  skill/command/helper surfaces.
- `.mcp.json` must be valid JSON and include a filesystem MCP scope covering
  the project root.
- `.codex/config.toml` must parse and include trusted project root plus
  project-scoped filesystem MCP.
- `openspec/config.yaml` must exist, and project-local `bin/openspec validate
  --all --strict` must pass.
- OPSX schemas and review-verdict helper must be reachable from the project.
- `.gitignore` must ignore `.runtime/`, `.artifacts/`, `.ai/`,
  `.codex/tmp/`, `.codex/auth.json`, `.codex/sessions/` and
  `.claude/settings.local.json`.
- Tracked files must not include runtime/auth/session paths.

## Failure Behavior

The verifier is fail-closed. A malformed config, missing symlink, broken
OpenSpec validation or unignored runtime/auth path is a failed check and a
non-zero exit.

## Verification

Focused verification uses a generated `.runtime` consumer project, one or more
intentional negative cases, `openspec validate --all --strict`, config parsers
and `git diff --check`.
