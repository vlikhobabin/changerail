# Design: bootstrap opt-in Codex auth link

## Context

Generated consumers already ignore `.codex/auth.json`, and runner preflight
accepts marker files under effective `CODEX_HOME`. The missing piece is an
explicit bootstrap action that creates a local symlink to an operator-selected
auth file without copying or printing secrets.

## Goals / Non-Goals

**Goals:**
- Add `--link-codex-auth <auth-json-path>` to `bin/bootstrap-project`.
- Create `<target>/.codex/auth.json` as a relative symlink to the supplied
  source.
- Fail before writing the link when the source is missing or is not a file.
- Show dry-run planning without exposing credential contents.

**Non-Goals:**
- Do not infer or copy credentials by default.
- Do not support multiple auth marker formats in bootstrap; runner may keep
  supporting `auth.toml`.
- Do not require auth for normal bootstrap verification.

## Decisions

- The option requires an explicit source path instead of guessing from
  `$HOME`. This avoids surprising credential linkage and keeps CI fixtures
  deterministic.
- The symlink is relative when possible, using the existing `create_symlink`
  helper, so generated local state remains portable if a workspace tree moves
  together.
- Bootstrap verifies the source path but never opens or prints file contents.

## Risks / Trade-offs

- [Risk] Requiring an explicit path is less convenient.
  → Mitigation: docs show the common `$HOME/.codex/auth.json` invocation.
- [Risk] A stale source can break later runner preflight.
  → Mitigation: runner stale-symlink checks remain fail-closed and diagnostics
  are improved in a later card-owned change.
