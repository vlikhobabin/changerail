# Repository Guidelines

## Purpose

This repository is `{{PROJECT_NAME}}`, a `{{PROJECT_KIND}}` project bootstrapped
with ChangeRail from `{{CHANGERAIL_ROOT}}`.

Treat this repository as public by default unless local project owners document
a stricter policy. Do not add secrets, credentials, customer data, runtime
traces, dumps, local databases or agent session state to tracked files.

## Project Scope

- Project root: `{{PROJECT_PATH}}`
- ChangeRail source of truth: `{{CHANGERAIL_ROOT}}`
- Project kind: `{{PROJECT_KIND}}`

Project source code, project-specific OpenSpec board, project rules, runtime
policy and domain verification belong in this repository. Reusable ChangeRail
methodology, skills, commands, schemas and helper wrappers belong in
`{{CHANGERAIL_ROOT}}`.

## Codex Setup

Use the project-local Codex profile when available. It scopes filesystem MCP to
`{{PROJECT_PATH}}` and discovers ChangeRail skills through `.codex/skills/`.

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
{{CHANGERAIL_ROOT}}/bin/verify-project {{PROJECT_PATH}}
git diff --check
```

Add project-specific tests here as the project evolves.

<!-- CHANGERAIL_SHARED_AGENTS_BEGIN source="{{CHANGERAIL_ROOT}}/AGENTS.shared.md" -->
{{CHANGERAIL_SHARED_AGENTS}}
<!-- CHANGERAIL_SHARED_AGENTS_END -->
