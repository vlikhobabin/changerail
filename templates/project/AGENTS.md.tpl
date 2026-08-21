# Repository Guidelines

## Purpose

This repository is `{{PROJECT_NAME}}`, a `{{PROJECT_PROFILE}}` project bootstrapped
with ChangeRail from {{CHANGERAIL_ROOT_LABEL}}.

Treat this repository as public by default unless local project owners document
a stricter policy. Do not add secrets, credentials, customer data, runtime
traces, dumps, local databases or agent session state to tracked files.

## Project Scope

- Project root: {{PROJECT_ROOT_LABEL}}
- ChangeRail source of truth: {{CHANGERAIL_ROOT_LABEL}}
- Project profile: `{{PROJECT_PROFILE}}`
- Surface profile: `{{SURFACES_PROFILE}}`
- Codex authority: `{{CODEX_POLICY}}`

{{TOPOLOGY_GUIDANCE}}

{{CODEX_AUTHORITY_GUIDANCE}}

Project source, board, rules, runtime policy and domain verification belong in
this repository. Reusable ChangeRail methodology and tooling belong in the
linked ChangeRail source of truth.

Board workflow guidance lives in ChangeRail
`docs/board-and-two-agent-feature-flow.md`; the reusable contract follows.

## Codex Setup

Use the project-local Codex profile when available. It scopes filesystem MCP to
this repository and discovers ChangeRail skills through `.codex/skills/`.

Do not commit Codex runtime files from `.codex/`. Public
`.codex/config.toml` and `.codex/skills/*` symlink-и are the only intended
tracked Codex files.

## Working Rules

- Prefer project-local helpers and verification commands documented here.
- Use `rg`/`rg --files` for search.
- Use `apply_patch` for manual file edits.
- Keep domain-specific instructions in this file; keep reusable ChangeRail behavior
  in the generated methodology section below.
- Do not commit generated runtime state, local reports, credentials or auth
  files.

## Verification Baseline

Run this baseline for ChangeRail wiring/config changes:

```bash
bin/openspec validate --all --strict
bin/verify-project .
git diff --check
```

Add project-specific tests here as the project evolves.

`bin/verify-project .` proves tracked static configuration, wiring and the
`project_doc_max_bytes` instruction budget; it is not effective Codex runtime
proof. Run `bin/verify-project . --runtime-diagnostics` only for explicit
runtime evidence with project-local `CODEX_HOME`. Raw probe output remains
ignored under `.runtime/changerail/diagnostics/`; share only its redacted
allowlisted summary and never credential values or local paths.

Generated verification policy lives in `openspec/config.yaml`. The selected
`{{SURFACES_PROFILE}}` profile treats Codex as `{{CODEX_SURFACE_STATE}}`, Claude
as `{{CLAUDE_SURFACE_STATE}}`, legacy MCP as `{{LEGACY_MCP_SURFACE_STATE}}`, and
stale legacy artifacts as `{{LEGACY_ARTIFACTS_SURFACE_STATE}}`. Project owners
may edit tracked policy to mark a surface `optional` only when that surface is
intentionally unused; optional missing surfaces can produce
`pass-with-diagnostics`, but targeted card-owned OpenSpec validation remains
mandatory and cannot be downgraded.

<!-- CHANGERAIL_SHARED_AGENTS_BEGIN source="{{CHANGERAIL_SHARED_SOURCE}}" -->
{{CHANGERAIL_SHARED_AGENTS}}
<!-- CHANGERAIL_SHARED_AGENTS_END -->
