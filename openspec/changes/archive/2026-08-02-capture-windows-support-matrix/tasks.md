## 1. Live Lab Probe

- [x] 1.1 Run `python3 scripts/windows-lab-probe.py run --inventory internal/windows-lab-inventory.json --json` against both ignored inventory hosts.
- [x] 1.2 Retain raw host evidence only under ignored `.runtime/changerail/` paths and record the sanitized report path.
- [x] 1.3 Confirm SSH access, non-interactive execution, fixture transfer,
  disposable root setup and cleanup passed or record a sanitized blocker.

## 2. Public Matrix

- [x] 2.1 Update `docs/compatibility.md` with the sanitized two-host OS,
  filesystem, Git, Python, shell and privilege matrix.
- [x] 2.2 Update the board card with verification outcomes and downstream
  handoff notes.
- [x] 2.3 Run `python3 scripts/public-surface-scan.py`.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate capture-windows-support-matrix --strict`.
- [x] 3.2 Run `./bin/openspec validate --all --strict`.
- [x] 3.3 Run `git diff --check`.
