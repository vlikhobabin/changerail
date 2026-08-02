## 1. Refresh And Drift

- [x] 1.1 Implement generated Windows wiring refresh that updates only
  generated-owned artifacts and updates digest metadata.
- [x] 1.2 Extend verification/drift checks for stale generated copies and
  project-owned divergence.
- [x] 1.3 Report refresh remediation paths without silently overwriting
  project-owned files.

## 2. Rollback And Fallbacks

- [x] 2.1 Add current-run rollback tracking that removes only artifacts created
  by the failed run.
- [x] 2.2 Add explicit Windows symlink fallback opt-in with positive
  privilege/Developer Mode proof.
- [x] 2.3 Add explicit Windows junction fallback opt-in with link-aware cleanup
  and Git-safety preconditions.

## 3. Tests And Documentation

- [x] 3.1 Add or update smoke fixtures for refresh, stale copies,
  project-owned divergence, partial rollback, symlink fallback and junction
  fallback.
- [x] 3.2 Update docs for refresh, upgrade, fallback proof, cleanup and
  generated ownership semantics.
- [x] 3.3 Preserve POSIX bootstrap and verification regression coverage.

## 4. Verification

- [x] 4.1 Run `bin/openspec status --change add-windows-wiring-refresh-and-fallbacks --json`.
- [x] 4.2 Run `bin/openspec instructions apply --change add-windows-wiring-refresh-and-fallbacks --json`.
- [x] 4.3 Run `bin/openspec validate add-windows-wiring-refresh-and-fallbacks --strict`.
- [x] 4.4 Run focused bootstrap/verify smoke commands covering refresh,
  rollback and fallback gates.
- [x] 4.5 Run `git diff --check`.
- [x] 4.6 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.7 Run `python3 scripts/run-release-baseline.py`.
