## 1. Deterministic Fixtures

- [x] 1.1 Add focused Windows entrypoint smoke coverage for the supported `.cmd`
  wrapper inventory.
- [x] 1.2 Verify argv forwarding, cwd preservation, environment preservation
  and exit-code propagation with deterministic fixtures.
- [x] 1.3 Cover paths with spaces and non-ASCII characters.
- [x] 1.4 Add negative coverage for direct extensionless POSIX launch and
  implicit Bash assumptions as unsupported native Windows defaults.

## 2. Release Integration

- [x] 2.1 Add the focused entrypoint smoke to the primary Linux release
  baseline.
- [x] 2.2 Preserve existing Linux/POSIX helper regression coverage.
- [x] 2.3 Record live Windows smoke as passed evidence or as an explicit
  blocker/caveat when hosts are unavailable.

## 3. Verification

- [x] 3.1 Run `bin/openspec status --change test-native-windows-entrypoints --json`.
- [x] 3.2 Run `bin/openspec instructions apply --change test-native-windows-entrypoints --json`.
- [x] 3.3 Run the focused Windows entrypoint smoke command.
- [x] 3.4 Run `bin/openspec validate test-native-windows-entrypoints --strict`.
- [x] 3.5 Run `bin/openspec validate --all --strict`.
- [x] 3.6 Run `git diff --check`.
- [x] 3.7 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.8 Run `python3 scripts/run-release-baseline.py`.

## Verification Notes

- Focused smoke `python3 scripts/smoke-windows-entrypoints.py --json` passed:
  49/49 checks, including supported `.cmd` inventory, selector routing, argv,
  cwd, environment, exit-code and spaces/non-ASCII fixture coverage.
- Full baseline `python3 scripts/run-release-baseline.py` passed: 28/28 steps,
  including the new Windows entrypoint smoke, Ruff, CI contract smoke,
  public-surface current/history scans and Linux/POSIX helper regression
  checks.
- Live Windows host smoke was not run from this Linux workspace. This card
  records that as an explicit caveat and does not claim live host coverage;
  later series cards own live automated smoke and end-to-end host proof.
