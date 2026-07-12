## Context

The existing templates render `{{PROJECT_PATH}}` into `AGENTS.md`,
`.mcp.json`, `.codex/config.toml` and `openspec/config.yaml`. Bootstrap then
prints a `git add` command that includes those files. This is acceptable for
generic examples such as `/opt/example-project`, but it is not public-safe for
real consumer repositories.

## Goals / Non-Goals

**Goals:**
- Default generated tracked files are portable and do not contain the absolute
  consumer project path.
- Local absolute-path config is still available when an operator deliberately
  wants it.
- `verify-project` understands portable and local config models.

**Non-Goals:**
- Do not change ChangeRail's own repo-local `.codex/config.toml` path contract.
- Do not create consumer-specific domain policy.
- Do not rewrite historical archived artifacts.

## Decisions

- Add `--config-mode portable|local` to `bin/bootstrap-project`, defaulting to
  `portable`.
- Render portable templates with relative project scope (`.`) and prose such as
  "this repository" instead of absolute consumer paths. Local mode renders the
  absolute target path and prints an explicit warning before the suggested
  `git add`.
- Add template placeholders for tracked project scope and human-readable
  project root text so docs and configs do not have to share the same value.
- Update `verify-project` to treat `.` and the project absolute path as valid
  filesystem scopes, and to accept either an absolute trust entry or a portable
  `.` trust entry in Codex config.

## Risks / Trade-offs

- [Risk] Relative scope relies on tools launching from the consumer project
  root. Mitigation: docs and generated AGENTS guidance tell operators to use
  project-local launchers and verification checks validate the model.
- [Risk] Existing consumers may still use local absolute config. Mitigation:
  verifier supports both models while bootstrap defaults to portable for new
  public-safe output.
