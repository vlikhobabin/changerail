## 1. Harness And Protocol

- [x] 1.1 Add `scripts/windows-lab-probe.py` with sample dry-run, ignored
  inventory validation and sanitized report generation.
- [x] 1.2 Document the Windows lab protocol, ignored inventory fields,
  disposable workspace rules, no-elevation rule, timeouts, cleanup and evidence
  retention in `docs/compatibility.md`.
- [x] 1.3 Ensure tracked docs and harness messages use only
  `windows-host-a`/`windows-host-b` and do not expose raw host identity.

## 2. Verification

- [x] 2.1 Run `python3 scripts/windows-lab-probe.py dry-run --sample --json`.
- [x] 2.2 Run `./bin/openspec validate establish-windows-lab-protocol --strict`.
- [x] 2.3 Run `git diff --check`.
