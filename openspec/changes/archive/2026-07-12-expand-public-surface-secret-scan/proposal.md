## Why

The public-surface scanner centralizes path leak checks, but it currently only
detects non-generic `/opt/*` paths. Public release gates also need to detect
common secret assignments, home paths and historical leaks without printing
secret values.

## What Changes

- Extend `scripts/public-surface-scan.py` with secret-like assignment and
  Linux/macOS/Windows home path checks.
- Add an optional reachable-history scan mode with redacted findings.
- Add self-test fixtures for allowed generic examples, secret assignments,
  private paths and historical leaks.
- Run the strengthened scan in CI/public release verification.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-agent-methodology`: public-safety verification includes secret,
  home-path and history scanning.
- `changerail-release-ci`: CI runs the strengthened scanner.

## Impact

- `scripts/public-surface-scan.py`
- `.github/workflows/changerail-ci.yml`
- `AGENTS.md`
- `AGENTS.shared.md`
- `docs/release-discipline.md`
