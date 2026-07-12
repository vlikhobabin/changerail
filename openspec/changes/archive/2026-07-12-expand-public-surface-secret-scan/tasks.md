## 1. Scanner

- [x] 1.1 Add secret-like assignment and home path detection to
  `scripts/public-surface-scan.py`.
- [x] 1.2 Add redacted finding output for secret values.
- [x] 1.3 Add `--history` mode for reachable git history scans.

## 2. Fixtures And CI

- [x] 2.1 Extend self-test fixtures for allowed examples, token-like
  assignments, home paths and historical leaks.
- [x] 2.1a Add a negative fixture proving values that merely contain `token` or
  `secret` are still reported unless they match an explicit placeholder value.
- [x] 2.1b Include tracked root public config/policy files in default scan roots
  and prove a token-like assignment in root `.mcp.json` fails the default scan.
- [x] 2.2 Update CI and release smoke checks to require the strengthened scan.

## 3. Docs And Checks

- [x] 3.1 Update public-safety verification docs in `AGENTS.md`,
  `AGENTS.shared.md` and release docs.
- [x] 3.2 Run `python3 scripts/public-surface-scan.py --self-test`.
- [x] 3.3 Run `python3 scripts/public-surface-scan.py --history`.
- [x] 3.4 Run `./bin/openspec validate expand-public-surface-secret-scan --strict`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile scripts/public-surface-scan.py scripts/smoke-release-ci.py` passed.
- `python3 scripts/public-surface-scan.py --self-test` passed with
  `PUBLIC_SURFACE_SCAN_SELF_TEST_OK`; the fixture verifies default roots catch a
  token-like assignment in root `.mcp.json` and redact its value.
- `python3 scripts/public-surface-scan.py --json` passed with 0 findings across
  394 default public-root files, including root config and policy files.
- `python3 scripts/public-surface-scan.py --history --json` passed with 0
  findings across reachable history for the same default roots.
- `python3 scripts/smoke-release-ci.py` passed with 31/31 checks.
- `./bin/openspec validate expand-public-surface-secret-scan --strict` passed.
- `git diff --check` passed.
- RED evidence is not applicable: this is scanner/gate hardening. The
  self-test creates negative current-tree and history fixtures, verifies secret
  values are redacted, and rejects broad token/secret substring placeholders,
  so it would fail if the new detection regressed.
