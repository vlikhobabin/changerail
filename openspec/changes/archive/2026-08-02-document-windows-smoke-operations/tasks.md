## 1. Operator Documentation

- [x] 1.1 Update Windows compatibility guidance with local matrix execution,
  live two-host execution and repeat-after-cleanup commands.
- [x] 1.2 Document sanitized evidence retention, ignored inventory, blocker and
  caveat handling for `windows-host-a` and `windows-host-b`.
- [x] 1.3 Document that local matrix success is not a live two-host support
  claim.

## 2. Release And CI Guidance

- [x] 2.1 Update release guidance to include the platform-neutral Windows smoke
  matrix in local baseline and CI inventory.
- [x] 2.2 Document the future Windows CI path as secure runner-local
  configuration without committing SSH targets, credentials or raw reports.

## 3. Verification

- [x] 3.1 Run `bin/openspec status --change document-windows-smoke-operations --json`.
- [x] 3.2 Run `bin/openspec instructions apply --change document-windows-smoke-operations --json`.
- [x] 3.3 Run `bin/openspec validate document-windows-smoke-operations --strict`.
- [x] 3.4 Run docs/config baseline checks from `AGENTS.md`:
  `python3 -m json.tool .mcp.json`, TOML parse for `.codex/config.toml` and
  `git diff --check`.
- [x] 3.5 Run `python3 scripts/public-surface-scan.py`.
