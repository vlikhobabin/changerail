## 1. Profile Model And CLI

- [x] 1.1 Add a normalized project/surface/Codex-policy model and validate all
  combinations before target mutation.
- [x] 1.2 Add canonical CLI flags, legacy `--kind` mapping and dry-run profile
  reporting with conflict/unknown negative paths.

## 2. Rendering And Verification

- [x] 2.1 Render topology-specific guidance and surface policy without creating
  domain-specific source or child repositories.
- [x] 2.2 Render safe-interactive by default and trusted-automation only after
  explicit selection.
- [x] 2.3 Extend `verify-project` with declared profile consistency and legacy
  all-surfaces compatibility checks.

## 3. Regression Evidence And Docs

- [x] 3.1 Add profile matrix fixtures that fail against the current label-only
  and implicit-full-access behavior before implementation.
- [x] 3.2 Cover invalid/conflicting combinations and fail-before-write behavior
  in bootstrap/verify smoke.
- [x] 3.3 Update bootstrap, adoption and compatibility docs for profile semantics
  and automation migration.

## 4. Verification

- [x] 4.1 Run `python3 scripts/smoke-bootstrap-project.py` and observe all profile
  checks pass.
- [x] 4.2 Run `python3 scripts/smoke-verify-project.py` and observe profile/severity
  checks pass.
- [x] 4.3 Run `./bin/openspec validate --all --strict`,
  `python3 scripts/public-surface-scan.py` and `git diff --check`.
