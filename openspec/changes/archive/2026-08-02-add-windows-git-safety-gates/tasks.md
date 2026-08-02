## 1. Git Safety Evidence

- [x] 1.1 Add deterministic Git safety fixture helpers for `git status
  --porcelain`, `git add --dry-run` and index inspection.
- [x] 1.2 Cover generated-copy, symlink fallback and junction fallback path
  classes with safe staging evidence.
- [x] 1.3 Add negative fixtures for ChangeRail source traversal, ignored runtime
  state, credential-like files and out-of-scope staged paths.

## 2. Cleanup And Ignore Boundaries

- [x] 2.1 Cover rename/update/uninstall or equivalent ownership transitions for
  Windows wiring paths.
- [x] 2.2 Cover partial cleanup so current-run-owned artifacts are removed
  without recursing through symlink or junction targets.
- [x] 2.3 Assert ignore rules remain minimal and project-owned source stays
  visible to Git safety checks.

## 3. Docs And Specs

- [x] 3.1 Update `docs/wiring-discovery.md` if Git safety commands,
  diagnostics or fallback proof wording changes.
- [x] 3.2 Sync delta specs for project verification, bootstrap, Windows native
  architecture and release CI.

## 4. Verification

- [x] 4.1 Run `bin/openspec status --change add-windows-git-safety-gates --json`.
- [x] 4.2 Run `bin/openspec instructions apply --change add-windows-git-safety-gates --json`.
- [x] 4.3 Run `bin/openspec validate add-windows-git-safety-gates --strict`.
- [x] 4.4 Run focused Windows wiring Git safety smoke.
- [x] 4.5 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 4.6 Run `python3 scripts/smoke-verify-project.py`.
- [x] 4.7 Run `git diff --check` and whitespace scan for untracked artifacts.
- [x] 4.8 Run `python3 scripts/public-surface-scan.py`.
