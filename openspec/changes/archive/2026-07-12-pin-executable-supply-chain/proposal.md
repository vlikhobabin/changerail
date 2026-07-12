## Why

ChangeRail's local Codex profile intentionally uses full filesystem access and
no approval prompts. Automatically executed MCP dependencies and CI actions
therefore need immutable, reviewable pins instead of floating package or major
tag references.

## What Changes

- Pin filesystem MCP npm package references to an exact version and track npm
  integrity metadata for all MCP npm packages launched by repo-local and
  generated configs.
- Validate generated MCP package pins in `verify-project`.
- Pin GitHub Actions workflow steps to immutable commit SHAs with readable
  version comments.
- Document update process for npm MCP pins and CI action SHAs.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-templates`: generated MCP config uses exact package pins.
- `changerail-project-verification`: verifier checks package pin policy.
- `changerail-release-ci`: CI workflow uses immutable action references.
- `changerail-release-discipline`: release docs define supply-chain pin update
  process.

## Impact

- `.mcp.json`
- `.codex/config.toml`
- `.github/workflows/changerail-ci.yml`
- `templates/project/mcp.json.tpl`
- `templates/project/codex-config.toml.tpl`
- `mcp-npm-lock.json`
- `bin/verify-project`
- `scripts/smoke-release-ci.py`
- `docs/compatibility.md`
- `docs/release-discipline.md`
