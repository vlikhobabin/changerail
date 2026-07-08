## 1. Bootstrap Command

- [x] 1.1 Add executable `bin/bootstrap-project`.
- [x] 1.2 Render template placeholders for project path, name, kind and OPSX
  root.
- [x] 1.3 Copy OpenSpec skeleton and create required symlink-и.
- [x] 1.4 Implement refuse-on-existing, `--dry-run` and `--backup-existing`.
- [x] 1.5 Run `verify-project` by default and print next steps.

## 2. Smoke And Docs

- [x] 2.1 Add `scripts/smoke-bootstrap-project.py`.
- [x] 2.2 Smoke positive bootstrap, dry-run no-write and refuse-on-existing.
- [x] 2.3 Update README/architecture docs for current bootstrap usage.

## 3. Verification

- [x] 3.1 Run `openspec validate "add-project-bootstrap-command" --strict`.
- [x] 3.2 Run `openspec validate --all --strict`.
- [x] 3.3 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile bin/bootstrap-project bin/verify-project
  scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py` passed.
- `python3 scripts/smoke-bootstrap-project.py` passed with 4/4 checks:
  positive bootstrap, dry-run no-write, refuse-on-existing and backup-existing.
- `openspec validate add-project-bootstrap-command --strict` passed.
- `openspec validate --all --strict` passed.
- `python3 -m json.tool .mcp.json` and delivery manifest JSON parsing passed.
- TOML parse for `.codex/config.toml` printed `TOML_OK`.
- `git diff --check` passed; separate untracked whitespace scan printed
  `JSON_TOML_DIFF_UNTRACKED_OK`.
- Targeted public-surface scan printed `PUBLIC_SURFACE_SCAN_OK`.
