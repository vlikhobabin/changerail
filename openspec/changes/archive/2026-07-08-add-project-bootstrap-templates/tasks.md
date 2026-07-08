## 1. Template Tree

- [x] 1.1 Add `templates/project/AGENTS.md.tpl` with project-local rules and
  generated OPSX methodology content.
- [x] 1.2 Add `templates/project/CLAUDE.md.tpl`.
- [x] 1.3 Add `templates/project/gitignore.tpl`.
- [x] 1.4 Add `templates/project/mcp.json.tpl`.
- [x] 1.5 Add `templates/project/codex-config.toml.tpl`.
- [x] 1.6 Add `templates/project/openspec/` skeleton.

## 2. Documentation

- [x] 2.1 Document placeholders and generated/symlink boundaries.
- [x] 2.2 Update README/architecture status for project templates.

## 3. Verification

- [x] 3.1 Run `openspec validate "add-project-bootstrap-templates" --strict`.
- [x] 3.2 Run `openspec validate --all --strict`.
- [x] 3.3 Run `git diff --check`.
- [x] 3.4 Run public-surface scan for private paths and raw runtime state.

## Verification Notes

- `openspec validate add-project-bootstrap-templates --strict` passed.
- `openspec validate --all --strict` passed.
- `git diff --check` passed; separate untracked whitespace scan printed
  `UNTRACKED_WHITESPACE_OK`.
- Targeted public-surface scan printed `PUBLIC_SURFACE_SCAN_OK`.
