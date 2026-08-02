## 1. Live Probe

- [x] 1.1 Run `python3 scripts/windows-runtime-wiring-probe.py run --inventory internal/windows-lab-inventory.json --json` against both ignored inventory hosts.
- [x] 1.2 Run the same live probe a second time after cleanup and record whether
  strategy conclusions match the primary run.
- [x] 1.3 Retain raw host output only under ignored `.runtime/changerail/` paths
  and record sanitized primary and repeatability report paths.

## 2. Public Comparison

- [x] 2.1 Update `docs/compatibility.md` with sanitized two-host runtime,
  wiring, Git, drift and wrapper invocation comparison results.
- [x] 2.2 Update the board card with verification outcomes, evidence paths,
  downstream handoff notes and archive paths.
- [x] 2.3 Run `python3 scripts/public-surface-scan.py`.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate capture-windows-runtime-wiring-results --strict`.
- [x] 3.2 Run `./bin/openspec validate --all --strict`.
- [x] 3.3 Run `git diff --check`.
