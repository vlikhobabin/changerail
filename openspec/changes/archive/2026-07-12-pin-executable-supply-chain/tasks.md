## 1. MCP Pins

- [x] 1.1 Pin filesystem MCP package references to
  `@modelcontextprotocol/server-filesystem@2026.7.10`.
- [x] 1.2 Add tracked MCP npm lock metadata for filesystem and Context7
  packages.
- [x] 1.3 Update generated consumer templates to use the same pins.

## 2. Verification And CI

- [x] 2.1 Update `bin/verify-project` to reject unpinned or unlocked MCP npm
  package args.
- [x] 2.1a Compare tracked MCP npm SRI metadata with npm registry
  `dist.integrity` during trusted setup verification.
- [x] 2.2 Pin GitHub Actions workflow action references to immutable SHAs with
  version comments.
- [x] 2.3 Update release CI smoke checks to reject mutable action tags.

## 3. Docs And Checks

- [x] 3.1 Document npm MCP and CI action update process.
- [x] 3.2 Run `python3 scripts/smoke-release-ci.py`.
- [x] 3.3 Run `python3 scripts/smoke-verify-project.py`.
- [x] 3.4 Run `./bin/openspec validate pin-executable-supply-chain --strict`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 -m json.tool .mcp.json` and `python3 -m json.tool mcp-npm-lock.json`
  passed.
- TOML parse for `.codex/config.toml` passed.
- `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py scripts/smoke-release-ci.py` passed.
- `python3 scripts/smoke-release-ci.py` passed with 30/30 checks.
- `python3 scripts/smoke-verify-project.py` passed with 8/8 checks, including
  a tampered MCP integrity fixture.
- Live trusted setup probe confirmed `bin/verify-project` compares tracked MCP
  integrity with npm registry metadata; source-repo-only symlink/gitignore
  checks are not applicable to `/opt/changerail` itself.
- `./bin/openspec validate pin-executable-supply-chain --strict` passed.
- `git diff --check` passed.
- RED evidence is not applicable: this is config/supply-chain hardening.
  Negative smoke fixtures now fail on mutable action tags and unpinned MCP
  package args and tampered registry integrity, so the checks would fail if the
  regression returned.
