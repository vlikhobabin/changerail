## 1. Gate Implementation

- [x] 1.1 Add executable `bin/verify-project`.
- [x] 1.2 Implement symlink resolution checks for Claude, Codex and helper
  wrappers.
- [x] 1.3 Implement `.mcp.json`, `.codex/config.toml` and
  `openspec/config.yaml` parsing checks.
- [x] 1.4 Run project-local `bin/openspec validate --all --strict`.
- [x] 1.5 Check helper/schema reachability and runtime/auth ignore policy.
- [x] 1.6 Support `--opsx-root` and `--aggregator-root`.

## 2. Verification Evidence

- [x] 2.1 Add focused positive and negative checks through the bootstrap smoke
  or a dedicated runtime fixture.
- [x] 2.2 Document verifier usage in README/architecture docs.

## 3. Verification

- [x] 3.1 Run `openspec validate "add-project-verify-gate" --strict`.
- [x] 3.2 Run `openspec validate --all --strict`.
- [x] 3.3 Run `python3 -m json.tool .mcp.json`.
- [x] 3.4 Run TOML parse for `.codex/config.toml`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py`
  passed.
- `python3 scripts/smoke-verify-project.py` passed with 2/2 checks: valid
  fixture passed and missing `.runtime/` ignore failed.
- `openspec validate add-project-verify-gate --strict` passed.
- `openspec validate --all --strict` passed.
- `python3 -m json.tool .mcp.json` passed.
- TOML parse for `.codex/config.toml` printed `TOML_OK`.
- `git diff --check` passed; separate untracked whitespace scan printed
  `JSON_TOML_DIFF_UNTRACKED_OK`.
