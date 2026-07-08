# Repository Guidelines

## Purpose

This repository is `{{PROJECT_NAME}}`, a `{{PROJECT_KIND}}` project bootstrapped
with OPSX from `{{OPSX_ROOT}}`.

Treat this repository as public by default unless local project owners document
a stricter policy. Do not add secrets, credentials, customer data, runtime
traces, dumps, local databases or agent session state to tracked files.

## Project Scope

- Project root: `{{PROJECT_PATH}}`
- OPSX source of truth: `{{OPSX_ROOT}}`
- Project kind: `{{PROJECT_KIND}}`

Project source code, project-specific OpenSpec board, project rules, runtime
policy and domain verification belong in this repository. Reusable OPSX
methodology, skills, commands, schemas and helper wrappers belong in
`{{OPSX_ROOT}}`.

## Codex Setup

Use the project-local Codex profile when available. It scopes filesystem MCP to
`{{PROJECT_PATH}}` and discovers OPSX skills through `.codex/skills/`.

Do not commit Codex runtime files from `.codex/`. Public
`.codex/config.toml` and `.codex/skills/*` symlink-и are the only intended
tracked Codex files.

## Working Rules

- Prefer project-local helpers and verification commands documented here.
- Use `rg`/`rg --files` for search.
- Use `apply_patch` for manual file edits.
- Keep domain-specific instructions in this file; keep reusable OPSX behavior
  in the generated methodology section below.
- Do not commit generated runtime state, local reports, credentials or auth
  files.

## Verification Baseline

Run this baseline for OPSX wiring/config changes:

```bash
bin/openspec validate --all --strict
{{OPSX_ROOT}}/bin/verify-project {{PROJECT_PATH}}
git diff --check
```

Add project-specific tests here as the project evolves.

<!-- OPSX_SHARED_AGENTS_BEGIN source="{{OPSX_ROOT}}/AGENTS.shared.md" -->
{{OPSX_SHARED_AGENTS}}
<!-- OPSX_SHARED_AGENTS_END -->
