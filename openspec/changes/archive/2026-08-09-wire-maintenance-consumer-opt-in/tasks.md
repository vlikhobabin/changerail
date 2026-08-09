## 1. Bootstrap and templates

- [x] 1.1 Add `--with-maintenance` to `bin/bootstrap-project`.
- [x] 1.2 Add opt-in maintenance policy/config/helper/ignore template rendering.
- [x] 1.3 Ensure default bootstrap output remains unchanged when
  `--with-maintenance` is absent.
- [x] 1.4 Extend native Windows generated-copy metadata to include maintenance
  helper ownership when opted in.

## 2. Verification

- [x] 2.1 Extend `bin/verify-project` to detect tracked maintenance opt-in
  signals.
- [x] 2.2 Verify complete maintenance helper, schema, config and ignore wiring
  for opted-in consumers.
- [x] 2.3 Keep non-opted-in consumers valid and skip maintenance checks as not
  configured.
- [x] 2.4 Add generated-copy freshness, stale and project-owned divergence
  checks for maintenance helper copies.
- [x] 2.5 Ensure verification does not run full maintenance scan during
  bootstrap verification.

## 3. Smoke coverage

- [x] 3.1 Add bootstrap smoke coverage for opted-in and non-opted-in consumers.
- [x] 3.2 Add verify-project smoke coverage for absent, complete and stale
  maintenance wiring.
- [x] 3.3 Add POSIX helper wiring and native Windows generated-copy refresh
  smoke coverage.

## 4. Verification

- [x] 4.1 Run `python3 -m py_compile` for changed bootstrap/verifier/test files.
- [x] 4.2 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 4.3 Run `python3 scripts/smoke-verify-project.py`.
- [x] 4.4 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.5 Run `./bin/openspec validate wire-maintenance-consumer-opt-in
  --strict`.
- [x] 4.6 Run `./bin/openspec validate --all --strict`.
- [x] 4.7 Run `git diff --check`.
