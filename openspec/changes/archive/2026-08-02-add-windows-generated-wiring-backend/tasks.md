## 1. Backend Selection And Ownership

- [x] 1.1 Add wiring backend selection that preserves POSIX symlink default and
  selects generated-copy by default for native Windows.
- [x] 1.2 Add generated wiring copy logic for command, skill and helper
  surfaces using the existing ChangeRail source-of-truth inventory.
- [x] 1.3 Record generated ownership metadata with project-relative destination,
  artifact kind, source identity, digest and owner state.

## 2. Reporting And Compatibility

- [x] 2.1 Update bootstrap dry-run output to report selected backend,
  generated ownership plan and skipped fallback reasons.
- [x] 2.2 Update wiring/compatibility docs for generated-copy Windows default
  while preserving POSIX symlink compatibility.
- [x] 2.3 Add or update focused bootstrap/wiring smoke fixtures for generated
  Windows default, ownership metadata and POSIX regression.

## 3. Verification

- [x] 3.1 Run `bin/openspec status --change add-windows-generated-wiring-backend --json`.
- [x] 3.2 Run `bin/openspec instructions apply --change add-windows-generated-wiring-backend --json`.
- [x] 3.3 Run `bin/openspec validate add-windows-generated-wiring-backend --strict`.
- [x] 3.4 Run focused bootstrap/wiring smoke commands covering generated backend
  and POSIX regression.
- [x] 3.5 Run `git diff --check`.
- [x] 3.6 Run `python3 scripts/public-surface-scan.py`.
