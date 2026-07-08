## 1. OpenSpec Skill Surface

- [x] 1.1 Add tracked `skills/openspec-*` lifecycle skill directories.
- [x] 1.2 Preserve MIT, OpenSpec author and generated-version metadata in imported skill frontmatter.
- [x] 1.3 Add `bin/openspec` wrapper pinned to OpenSpec CLI `1.3.0`.

## 2. Documentation

- [x] 2.1 Add OpenSpec lifecycle compatibility and sync-policy documentation.
- [x] 2.2 Update README, Claude notes and wiring docs for `openspec-*` skills and `bin/openspec`.

## 3. Verification

- [x] 3.1 Run `openspec validate "add-openspec-lifecycle-surface" --strict`.
- [x] 3.2 Run `/opt/opsx/bin/openspec --version`.
- [x] 3.3 Run public-surface scan for private paths in `skills/openspec-*` and `bin/openspec`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `openspec validate add-openspec-lifecycle-surface --strict` passed.
- `/opt/opsx/bin/openspec --version` printed `1.3.0`.
- `python3 scripts/smoke-wiring-discovery.py` passed with 118/118 checks,
  covering `openspec-*` skill symlinks and frontmatter.
- Targeted public-path scan returned no private path matches.
- `git diff --check` passed.
