## 1. Verifier And Drift Fixtures

- [x] 1.1 Extend generated Windows verifier smoke to cover missing generated
  artifacts in addition to valid, stale, diverged and refresh cases.
- [x] 1.2 Add drift smoke coverage that classifies stale or project-owned
  generated Windows wiring as `broken_wiring` with refresh diagnostics.
- [x] 1.3 Confirm generated wiring diagnostics use repository-relative paths
  and do not print credential contents, private hostnames or private Windows
  absolute paths.

## 2. Docs And Specs

- [x] 2.1 Update `docs/wiring-discovery.md` if verifier/drift diagnostics or
  refresh remediation wording changes.
- [x] 2.2 Sync delta specs for project verification, drift gate, wiring
  discovery and Windows native architecture.

## 3. Verification

- [x] 3.1 Run `bin/openspec status --change enforce-windows-wiring-verification --json`.
- [x] 3.2 Run `bin/openspec instructions apply --change enforce-windows-wiring-verification --json`.
- [x] 3.3 Run `bin/openspec validate enforce-windows-wiring-verification --strict`.
- [x] 3.4 Run `python3 scripts/smoke-verify-project.py`.
- [x] 3.5 Run focused drift smoke for generated valid/stale/diverged fixtures.
- [x] 3.6 Run `git diff --check` and whitespace scan for untracked artifacts.
- [x] 3.7 Run `python3 scripts/public-surface-scan.py`.
